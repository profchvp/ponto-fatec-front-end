
async function httpPost(url, body) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    mode: 'cors',
    body: JSON.stringify(body),
  });
  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;
  return { status: res.status, data };
}

async function httpGet(url) {
  const res = await fetch(url, { method: 'GET', mode: 'cors' });
  const isJson = res.headers.get('content-type')?.includes('application/json');
  const data = isJson ? await res.json() : null;
  return { status: res.status, data };
}

window.Api = { httpPost, httpGet };
