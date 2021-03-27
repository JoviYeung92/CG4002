import socketIOClient from 'socket.io-client';
import { GET_SOCKET } from '../reducers/Types';
import { SOCKET_API } from './ApiUrls';

export const getSocketConnection = () => (dispatch, getState) => {
    dispatch({
        type: GET_SOCKET,
        payload: socketIOClient(SOCKET_API),
    });
};