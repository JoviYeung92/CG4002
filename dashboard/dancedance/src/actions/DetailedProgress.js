import { PUSH_ACCURACY_FAQ, PUSH_MOVEMENT_FAQ } from "../reducers/Types";

export const getUserStats = (faqData) => (dispatch) => {
    dispatch({
        type: PUSH_ACCURACY_FAQ,
        payload: faqData
    })
};

export const pushUserStats = (formData) => (dispatch) => {
    dispatch({
        type: PUSH_MOVEMENT_FAQ,
        payload: faqData
    })
};