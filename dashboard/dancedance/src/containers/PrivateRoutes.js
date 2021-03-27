import React from "react";
import { Route, Redirect } from "react-router-dom";
import { useSelector, shallowEqual } from "react-redux";

import { LOGIN_ROUTE } from "../routes";

/**
 * See bug fix for rendering components on routes:
 * https://stackoverflow.com/questions/57408430/warning-you-should-not-use-route-component-and-route-render-in-the-same-rou
 *
 */
export const PrivateRoutes = ({ component: Component, ...rest }) => {
  /**
   * see comparison for mimicking mapStateToProps from HOC:
   * https://thoughtbot.com/blog/using-redux-with-react-hooks#:~:text=React%20Redux%20now%20includes%20its,state%20you're%20interested%20in.
   */
  const auth = useSelector((state) => state.Auth, shallowEqual);
  return (
    <Route
      {...rest}
      render={(props) => {
        if (auth.isLoading) {
          return <h2>Loading...</h2>;
        } else if (!auth.isAuthenticated) {
          return <Redirect to={LOGIN_ROUTE} />;
        } else {
          return <Component {...props} />;
        }
      }}
    />
  );
};

export default PrivateRoutes;