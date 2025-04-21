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

export const statusPlace = async (uuid) => {
    const response = await getAPICall(`/api/places/tpaystatus/${uuid}`);
    return response;
}

export const webhookPlace = async (data) => {
    const response = await postAPICall(`/api/webhook/tpay`, data);
    return response;
}

export const consultaTpayPlace = async (uuid, data) => {
    const response = await getAPICall(`/api/places/tpayconsulta/${uuid}`);
    return response;
}

export const tpayPlace = async (uuid) => {
    const response = await getAPICall(`/api/places/tpay/${uuid}`);
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

export const addDescuento = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/descuento/agregar`, data);
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

export const addGafete = async (uuid, uuid_place) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/gafete/agregar`);
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

export const applyCashPaymentGafete = async (uuid, uuid_place, uuid_px, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/gafete/${uuid_px}/pago`, data);
    return response;
}

export const aplicarPago = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/pago`, data);
    return response;
}

export const aplicarTransferencia = async (uuid, uuid_place, data) => {
    const response = await postAPICall(`/admin/solicitud/${uuid}/lugar/${uuid_place}/transfer`, data);
    return response;
}


export const validateCURPService = async (curp) => {
    const response = await getAPICall(`/api/get-curp-service/${curp}`);
    return response;
}