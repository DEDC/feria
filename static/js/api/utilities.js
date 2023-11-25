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