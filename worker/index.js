/**
 * Cloudflare Worker - Email Signup Handler
 *
 * Handles form submissions from the landing page and adds
 * contacts to the Resend audience.
 *
 * Environment variables needed (set in Cloudflare dashboard):
 * - RESEND_API_KEY
 * - RESEND_AUDIENCE_ID
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export default {
  async fetch(request, env, ctx) {
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
        // Check if it's a duplicate (already subscribed)
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
  },
};
