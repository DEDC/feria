import { url_dates, url_times } from '../api/endpoints.js'
import { getAPICall, postAPICall, patchAPICall, deleteAPICall } from '../api/api.js'

export const getAvailableDates = async () => {
    const response = await getAPICall(url_dates);
    return response;
}

export const getAvailableTimes = async (date) => {
    const response = await getAPICall(`${url_times}/${date}`);
    return response;
}

export const getPlaces = async (url) => {
    const response = await getAPICall(url);
    return response;
}

export const setPlaceTemp = async (uuid, data, zone) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/${zone}/lugar/temp`, data);
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