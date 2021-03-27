import DancerResults from './DancerResults';
import React, { useEffect, useMemo, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { useSelector, useDispatch } from "react-redux";
import { getRawSensorData } from "../actions/RawSensorData";
import { RealtimeLineGraph } from './RealtimeLineGraph';
import { ACCELERATIONA1, ROTATIONALV1, ROTATIONALV1GRAPH, ACCELERATION1GRAPH } from './Constants';
import { Tabs, Tab } from 'react-bootstrap';
import { EvaluationGraphTab } from './EvaluationGraphTab';


export const EvaluationMode = () => {
    return (
        <div>
            <Container fluid>
                <Row>
                    <Col className="card">
                        <DancerResults dancerNum={1} />
                    </Col>
                    <Col className="card">
                        <DancerResults dancerNum={2} />
                    </Col>
                    <Col className="card">
                        <DancerResults dancerNum={3} />
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <EvaluationGraphTab dancer={1} />
                    </Col>
                    <Col>
                        <EvaluationGraphTab dancer={2} />
                    </Col>
                    <Col>
                        <EvaluationGraphTab dancer={3} />
                    </Col>
                </Row>
            </Container>
        </div>
    )


}

export default EvaluationMode;