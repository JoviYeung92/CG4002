import { PUSH_ACCURACY_FAQ, PUSH_MOVEMENT_FAQ } from "./Types"

const initialState = {
}

export default (state = initialState, action) => {
    switch (action.type) {
        case PUSH_ACCURACY_FAQ:
            return {
                ...state,
                accuracyFaq: action.payload
            }
        case PUSH_MOVEMENT_FAQ:
            return {
                ...state,
                movementFaq: action.payload
            }
        default:
            return state;
    }
}