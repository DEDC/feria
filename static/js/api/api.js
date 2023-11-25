// axios.interceptors.request.use((config) => {
//     console.log('loaddingg')
//     return config;
// }, (error) => {
//     // trigger 'loading=false' event here
//     return Promise.reject(error);
// });

// axios.interceptors.response.use((response) => {
//     console.log('trrtminpp')
//     return response;
// }, (error) => {
//     // trigger 'loading=false' event here
//     return Promise.reject(error);
// });

// API Axios Get Call.
export const getAPICall = (url, config) => {
    return axios.get(url, config);
}
// API Axios Post Call.
export const postAPICall = (url, data, config) => {
    return axios.post(url, data, config);
}
// API Axios Put Call.
export const putAPICall = (url, data) => {
    return axios.put(url, data);
}
// API Axios Delete Call.
export const deleteAPICall = (url, config) => {
    return axios.delete(url, config);
}

export const patchAPICall = (url, data, config) => {
    return axios.patch(url, data, config);
}