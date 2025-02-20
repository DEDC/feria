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

export const pdfPlace = async (uuid, data) => {
    const response = await getAPICall(`/api/places/pdfcpatura/${uuid}`);
    return response;
}

export const tpayPlace = async (uuid, data) => {
    const response = await getAPICall(`/api/places/tpay/${uuid}`, data);
    return response;
}

export const setPlace = async (uuid, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/set`, data);
    return response;
}

export const addTerraza = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/terraza/agregar`, data);
    return response;
}

export const addBigTerraza = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/terraza_grande/agregar`, data);
    return response;
}

export const addAlcohol = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/alcohol/agregar`, data);
    return response;
}

export const deleteItem = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/item/${uuid_place}/eliminar`, data);
    return response;
}

export const deletePlace = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/eliminar`, data);
    return response;
}


export const validateCURPService = async (curp) => {
    const response = await getAPICall(`/api/get-curp-service/${curp}`);
    return response;
}