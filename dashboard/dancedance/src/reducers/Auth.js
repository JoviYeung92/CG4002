import {USER_LOADED, USER_LOADING, REGISTER_FAILED, REGISTER_SUCCESS, LOGIN_FAILED, LOGIN_SUCCESS, LOGOUT_SUCCESS, AUTH_ERROR} from "./Types"

const initialState = {
    isAuthenticated: null,
    isLoading: false,
    user: localStorage.getItem("username")
}

export default (state = initialState, action) => {
    switch (action.type) {
        case USER_LOADING:
            return {
                ...state,
                isLoading: true,
            }
        case USER_LOADED:
            return {
                ...state,
                isAuthenticated: true,
                isLoading: false,
                user: action.payload
            }
        case REGISTER_SUCCESS:
        case LOGIN_SUCCESS:
            localStorage.setItem("username", action.payload);
            return {
                ...state,
                isAuthenticated: true,
                isLoading: false,
                user: action.payload

            }
        case REGISTER_FAILED:
        case LOGOUT_SUCCESS:
        case AUTH_ERROR:
        case LOGIN_FAILED:
            localStorage.removeItem("username");
            return {
                ...state,
                token: null,
                user: null,
                isAuthenticated: false,
                isLoading: false,
            }
        default:
            return state;
    }
}