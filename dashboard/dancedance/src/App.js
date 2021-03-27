import React, { Fragment, useEffect } from 'react';
import { HashRouter as Router, Switch, Route } from "react-router-dom";
import { LOGIN_ROUTE, DASHBOARD_ROUTE, EVALUATION_MODE_ROUTE, REGISTER_ROUTE, DETAILEDPROGRESS_ROUTE, PRACTICEMODE_ROUTE } from './routes';
import { Login } from './containers/Login';
import { Dashboard } from './containers/Dashboard';
import Navbar from './containers/Navbar';
import EvaluationMode from './components/EvaluationMode';
import StoreProvider from './storeProvider/storeProvider';
import PrivateRoutes from './containers/PrivateRoutes';
import { Register } from './containers/Register';
import { DetailedProgress } from './components/DetailedProgress';
import { PracticeMode } from './components/PracticeMode';

const App = () => {
  return (
    <StoreProvider>
      <Router>
        <Fragment>
          <Navbar />
            <Switch>
              <Route exact path={LOGIN_ROUTE} component={Login} />
              <Route exact path={REGISTER_ROUTE} component={Register} />
              <PrivateRoutes exact path={DASHBOARD_ROUTE} component={Dashboard} />
              <PrivateRoutes exact path={EVALUATION_MODE_ROUTE} component={EvaluationMode} />
              <PrivateRoutes exact path={DETAILEDPROGRESS_ROUTE} component={DetailedProgress} />
              <PrivateRoutes exact path={PRACTICEMODE_ROUTE} component={PracticeMode} />
            </Switch>
        </Fragment>
      </Router>

    </StoreProvider>
  )
}

export default App
