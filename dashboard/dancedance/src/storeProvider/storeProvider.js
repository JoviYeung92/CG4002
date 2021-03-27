import React, { useEffect } from "react";
import { Provider } from "react-redux";
import { loadUser } from "../actions/Auth";
import { getSocketConnection } from "../actions/Socket";
import store from "./store";

export const StoreProvider = (props) => {
  useEffect(()=> {
    store.dispatch(getSocketConnection());
    store.dispatch(loadUser());
  }, [])
  const { children } = props;
  return <Provider store={store}>{children}</Provider>;
};

export default StoreProvider;