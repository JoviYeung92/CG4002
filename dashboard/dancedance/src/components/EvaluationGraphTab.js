import React, { useState, Fragment } from 'react';
import { RealtimeLineGraph } from './RealtimeLineGraph';
import { ACCELERATIONX, ROLL, PITCH, YAW, ROLLGRAPH, ACCELERATIONXGRAPH, PITCHGRAPH, YAWGRAPH, ABSOLUTE_AVG_ACCELERATION, ABSOLUTE_AVG_ACCELERATION_GRAPH, MINIPREDICTIONGRAPH } from './Constants';
import { Tabs, Tab } from 'react-bootstrap';
import { EvalMiniPredictiongraph } from './EvalMiniPredictionGraph';

export const EvaluationGraphTab = ({ dancer }) => {
    const [key, setKey] = useState(PITCH);
    return (
        <Fragment>
            <Tabs
                activeKey={key}
                onSelect={(k) => setKey(k)}
            >
                <Tab eventKey={PITCH} title="PITCH">
                    <RealtimeLineGraph
                        dancer={dancer}
                        graphType={PITCHGRAPH} />
                </Tab>
                <Tab eventKey={ABSOLUTE_AVG_ACCELERATION} title="JERKINESS">
                    <RealtimeLineGraph
                        dancer={dancer}
                        graphType={ABSOLUTE_AVG_ACCELERATION_GRAPH} />
                </Tab>
                <Tab eventKey={MINIPREDICTIONGRAPH} title="OVERALL PREDICTIONS">
                    <EvalMiniPredictiongraph
                        dancer={dancer}/>
                </Tab>
            </Tabs>

        </Fragment>
    )
}