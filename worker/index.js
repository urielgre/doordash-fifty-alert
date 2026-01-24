/**
 * Cloudflare Worker - Email Signup & Feedback Handler
 *
 * Handles:
 * - POST / - Subscribe email to audience
 * - POST /feedback - Send feedback/suggestions to admin
 *
 * Environment variables needed:
 * - RESEND_API_KEY
 * - RESEND_AUDIENCE_ID
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// Note: Resend free tier can only send to verified emails
// Using the Resend account email, feedback forwarded to secondary
const ADMIN_EMAIL = 'urielgsn@gmail.com';
const FORWARD_EMAIL = 'GVDEV1200@gmail.com';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    // Only accept POST
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
      });
    }

    // Route to appropriate handler
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
        to: ADMIN_EMAIL,
        reply_to: email || undefined,
        subject: `[50-Point Alerts] New ${type || 'Feedback'}: ${message.slice(0, 50)}...`,
        html: `
          <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #FF3008;">New ${type || 'Feedback'} Received</h2>
            <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
              <p style="margin: 0; font-size: 16px; line-height: 1.6;">${message.replace(/\n/g, '<br>')}</p>
            </div>
            <p style="color: #666; font-size: 14px;"><strong>From:</strong> ${email}</p>
            <p style="color: #999; font-size: 12px; margin-top: 16px;">Please forward to: ${FORWARD_EMAIL}</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">Sent from 50-Point Alerts feedback form</p>
          </div>
        `,
        text: `New ${type || 'Feedback'}:\n\n${message}\n\nFrom: ${email}\n\nPlease forward to: ${FORWARD_EMAIL}`,
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
