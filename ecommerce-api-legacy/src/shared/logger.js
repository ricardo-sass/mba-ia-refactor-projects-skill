function sanitize(details) {
  const safe = { ...details };
  delete safe.card;
  delete safe.password;
  delete safe.paymentGatewayKey;
  if (safe.error instanceof Error) safe.error = safe.error.message;
  return safe;
}

function info(message, details = {}) {
  const safe = sanitize(details);
  const suffix = Object.keys(safe).length ? ` ${JSON.stringify(safe)}` : '';
  console.log(`[INFO] ${message}${suffix}`);
}

function error(message, details = {}) {
  console.error(`[ERROR] ${message} ${JSON.stringify(sanitize(details))}`);
}

module.exports = { info, error };
