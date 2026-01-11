const DEFAULT_BASE_URL = 'http://localhost:5050/api/';
const baseURL = (() => {
    const envURL = import.meta.env['VITE_API_BASE_URL'] as string | undefined;
    const url = (envURL ?? DEFAULT_BASE_URL).trim();
    return url.endsWith('/') ? url : `${url}/`;
})();

export default baseURL;