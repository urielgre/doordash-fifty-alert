/**
 * Cloudflare Worker - Email Signup, Unsubscribe & Feedback Handler
 *
 * Handles:
 * - POST / - Subscribe email to audience
 * - POST /unsubscribe - Unsubscribe email from audience
 * - POST /feedback - Send feedback/suggestions to admin
 *
 * Environment variables needed:
 * - RESEND_API_KEY
 * - RESEND_AUDIENCE_ID
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;',
  };
  return text.replace(/[&<>"']/g, (char) => map[char]);
}

// Admin emails loaded from environment variables (set in Cloudflare dashboard)
// ADMIN_EMAIL - Primary admin email for receiving feedback
// FORWARD_EMAIL - Secondary email to forward feedback to

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // Route to appropriate handler
    if (url.pathname === '/unsubscribe') {
      // Handle both GET (with email param) and POST
      if (request.method === 'GET') {
        const email = url.searchParams.get('email');
        if (email) {
          return handleUnsubscribe(email, env);
        }
        // Return unsubscribe form HTML
        return new Response(getUnsubscribePageHTML(), {
          headers: { ...CORS_HEADERS, 'Content-Type': 'text/html' },
        });
      } else if (request.method === 'POST') {
        const body = await request.json();
        return handleUnsubscribe(body.email, env);
      }
    }

    // Only accept POST for other routes
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/feedback') {
      return handleFeedback(request, env);
    } else {
      return handleSignup(request, env);
    }
  },
};

async function handleSignup(request, env) {
  try {
    const body = await request.json();
    const email = body.email?.trim().toLowerCase();

    // Validate email
    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: 'Invalid email address' }), {
        status: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    // Add to Resend audience
    const response = await fetch(
      `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          unsubscribed: false,
        }),
      }
    );

    const result = await response.json();

    if (!response.ok) {
      if (result.message?.includes('already exists')) {
        return new Response(JSON.stringify({
          success: true,
          message: 'Already subscribed!'
        }), {
          status: 200,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
      }

      console.error('Resend error:', result);
      return new Response(JSON.stringify({ error: 'Failed to subscribe' }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Successfully subscribed!'
    }), {
      status: 200,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: 'Server error' }), {
      status: 500,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
}

async function handleFeedback(request, env) {
  try {
    const body = await request.json();
    const { message, email, type } = body;

    // Validate message
    if (!message || message.trim().length < 3) {
      return new Response(JSON.stringify({ error: 'Please enter a message' }), {
        status: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    // Send email to admin
    const response = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: '50-Point Alerts <onboarding@resend.dev>',
        to: env.ADMIN_EMAIL,
        reply_to: email || undefined,
        subject: `[50-Point Alerts] New ${type || 'Feedback'}: ${message.slice(0, 50)}...`,
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #FF3008;">New ${escapeHtml(type || 'Feedback')} Received</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
              <p style="margin: 0; font-size: 16px; line-height: 1.6;">${escapeHtml(message).replace(/\n/g, '<br>')}</p>
            </div>
            <p style="color: #666; font-size: 14px;"><strong>From:</strong> ${escapeHtml(email || 'Anonymous')}</p>
            <p style="color: #999; font-size: 12px; margin-top: 16px;">Please forward to: ${env.FORWARD_EMAIL}</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">Sent from 50-Point Alerts feedback form</p>
          </div>
        `,
        text: `New ${type || 'Feedback'}:\n\n${message}\n\nFrom: ${email}\n\nPlease forward to: ${env.FORWARD_EMAIL}`,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Email error:', error);
      return new Response(JSON.stringify({ error: 'Failed to send feedback' }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'Feedback sent! Thanks for your input.'
    }), {
      status: 200,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: 'Server error' }), {
      status: 500,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
}

async function handleUnsubscribe(email, env) {
  try {
    if (!email || !email.includes('@')) {
      return new Response(JSON.stringify({ error: 'Invalid email address' }), {
        status: 400,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    const cleanEmail = email.trim().toLowerCase();

    // Update contact to unsubscribed status
    const response = await fetch(
      `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts/${encodeURIComponent(cleanEmail)}`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${env.RESEND_API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          unsubscribed: true,
        }),
      }
    );

    if (!response.ok) {
      const result = await response.json();
      // If contact not found, that's fine - they're not subscribed anyway
      if (response.status === 404) {
        return new Response(JSON.stringify({
          success: true,
          message: 'You have been unsubscribed.'
        }), {
          status: 200,
          headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
        });
      }
      console.error('Resend error:', result);
      return new Response(JSON.stringify({ error: 'Failed to unsubscribe' }), {
        status: 500,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    return new Response(JSON.stringify({
      success: true,
      message: 'You have been unsubscribed successfully.'
    }), {
      status: 200,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });

  } catch (error) {
    console.error('Error:', error);
    return new Response(JSON.stringify({ error: 'Server error' }), {
      status: 500,
      headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
    });
  }
}

function getUnsubscribePageHTML() {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Unsubscribe - 50-Point Alerts</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f7f7f7;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .card {
      background: white;
      border-radius: 12px;
      padding: 40px;
      max-width: 400px;
      width: 100%;
      box-shadow: 0 4px 20px rgba(0,0,0,0.08);
      text-align: center;
    }
    h1 { color: #1F1F1F; font-size: 24px; margin-bottom: 12px; }
    p { color: #666; font-size: 14px; margin-bottom: 24px; }
    input {
      width: 100%;
      padding: 14px 16px;
      border: 2px solid #e0e0e0;
      border-radius: 8px;
      font-size: 16px;
      margin-bottom: 16px;
    }
    input:focus { outline: none; border-color: #FF3008; }
    button {
      width: 100%;
      padding: 14px;
      background: #FF3008;
      color: white;
      border: none;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 600;
      cursor: pointer;
    }
    button:hover { background: #E02A07; }
    button:disabled { background: #ccc; cursor: not-allowed; }
    .message { margin-top: 16px; padding: 12px; border-radius: 6px; font-size: 14px; }
    .success { background: #d4edda; color: #155724; }
    .error { background: #f8d7da; color: #721c24; }
    .back-link { margin-top: 20px; }
    .back-link a { color: #FF3008; text-decoration: none; font-size: 14px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Unsubscribe</h1>
    <p>Enter your email to unsubscribe from 50-Point Alerts.</p>
    <form id="unsubscribe-form">
      <input type="email" id="email" placeholder="your@email.com" required>
      <button type="submit" id="submit-btn">Unsubscribe</button>
    </form>
    <div id="message" class="message" style="display: none;"></div>
    <div class="back-link">
      <a href="https://urielgre.github.io/doordash-fifty-alert/">Back to 50-Point Alerts</a>
    </div>
  </div>
  <script>
    document.getElementById('unsubscribe-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('submit-btn');
      const msg = document.getElementById('message');
      const email = document.getElementById('email').value;

      btn.disabled = true;
      btn.textContent = 'Processing...';
      msg.style.display = 'none';

      try {
        const res = await fetch('/unsubscribe', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();

        msg.style.display = 'block';
        if (data.success) {
          msg.className = 'message success';
          msg.textContent = data.message;
          document.getElementById('email').value = '';
        } else {
          msg.className = 'message error';
          msg.textContent = data.error || 'Something went wrong';
        }
      } catch (err) {
        msg.style.display = 'block';
        msg.className = 'message error';
        msg.textContent = 'Network error. Please try again.';
      }

      btn.disabled = false;
      btn.textContent = 'Unsubscribe';
    });
  </script>
</body>
</html>`;
}
