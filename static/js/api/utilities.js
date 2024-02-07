import { url_dates, url_times, url_nave_1 } from '../api/endpoints.js'
import { getAPICall, postAPICall, patchAPICall, deleteAPICall } from '../api/api.js'

export const getAvailableDates = async () => {
    const response = await getAPICall(url_dates);
    return response;
}

export const getAvailableTimes = async (date) => {
    const response = await getAPICall(`${url_times}/${date}`);
    return response;
}

export const getNave1Data = async (date) => {
    const response = await getAPICall(url_nave_1);
    return response;
}

export const setPlaceTemp = async (uuid, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/temp`, data);
    return response;
}

export const unsetPlaceTemp = async (uuid, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/unset/temp`, data);
    return response;
}

export const setPlace = async (uuid, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/set`, data);
    return response;
}