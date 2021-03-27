import React, { useState, useEffect, Fragment } from 'react';
import { useSelector } from "react-redux";
import { Container, Row, Col } from "react-bootstrap";
import ReactSpeedometer from "react-d3-speedometer"
import { GOOD_FLEXIBILITY, GREAT_FLEXIBILITY, HIGH_IMPACT_AEROBIC, LOW_IMPACT_AEROBIC, MEDIUM_IMPACT_AEROBIC, POOR_FLEXIBILITY, WAITING } from './Constants';

export const DancerResults = ({dancerNum}) => {
    const [results, setResults] = useState({
        dance: "none",
        position: "none"
    })
    const [rawData, setRawData] = useState({});
    const [calories, setCalories] = useState(0);
    const [weight, setWeight] = useState(0);
    const [flexi, setFlexi] = useState(-1);

    const getFinalPrediction = (prediction) => {
        if (dancerNum === 1) {
            setResults({
                dance: prediction.Dancer1Prediction,
                position: prediction.Dancer1Position
            })
        } else if (dancerNum === 2) {
            setResults({
                dance: prediction.Dancer2Prediction,
                position: prediction.Dancer2Position
            })
        } else if (dancerNum === 3) {
            setResults({
                dance: prediction.Dancer3Prediction,
                position: prediction.Dancer3Position
            })
        }
    }

    const getPrediction = (prediction) => {
        if (prediction.DancerNumber === dancerNum) {
            setResults({
                danceMove: prediction.DanceMovePrediction
            })
            setFlexi(prediction.DanceMovePrediction !== results.danceMove ? -1 : flexi);
        }
    }

    const checkMET = (rawData) => {
        const totalAbs = Math.abs(rawData.Roll) + Math.abs(rawData.Pitch) + Math.abs(rawData.Yaw);
        if (totalAbs > 50 && totalAbs <= 400) {
            return LOW_IMPACT_AEROBIC;
        } else if (totalAbs > 400 && totalAbs <= 600) {
            return MEDIUM_IMPACT_AEROBIC;
        } else if (totalAbs > 600) {
            return HIGH_IMPACT_AEROBIC;
        }
    }

    useEffect(() => {
        if (rawData.Dancer === dancerNum) {
            const METvalue = checkMET(rawData);
            setCalories(METvalue * weight);
            setFlexi(Math.abs(rawData.Pitch))
        }
    }, [rawData])

    const getSensorData = (data) => {
        setRawData(data)
    }

    const checkFlexi = () => {
        if (flexi === -1) {
            return WAITING;
        } else if (flexi > 0 && flexi <= 1) {
            return POOR_FLEXIBILITY;
        } else if (flexi > 1 && flexi <= 2.5 ) {
            return GOOD_FLEXIBILITY;
        } else if (flexi > 2.5) {
            return GREAT_FLEXIBILITY;
        }
    }
    const setFlexiColor = () => {
        if (flexi === -1) {
            return "black";
        } else if (flexi > 0 && flexi <= 1) {
            return "red";
        } else if (flexi > 1 && flexi <= 2.5 ) {
            return "green";
        } else if (flexi > 2.5) {
            return "green";
        }
    }
    const weightInputHandler = (e) => {
        setWeight(e.target.value);
    }

    const socket = useSelector((state) => state.Socket.socket)
    useEffect(() => {
        if (socket !== null) {
            socket.on('realRawSensorData', getSensorData);
            socket.on('realFinalPrediction', getFinalPrediction);
            // socket.on('realPrediction', getPrediction);
        }
    }, [socket])

    return (
        <Fragment>
            <Row>
                <Col>
                    <h4>Dancer {dancerNum} </h4>
                    <h3>Position: {results.position}</h3>
                    <h3>Dance Move: {results.dance}</h3>
                    <h3 style={{color: `${setFlexiColor()}`}}>Flexibility: {checkFlexi()}</h3>
                    <img src = {process.env.PUBLIC_URL + `/img/dancer${dancerNum}.png`} style={{width:"100px", height:"100px"}}/>
                </Col>
                <Col>
                    <strong style={{ marginTop: '20px' }}>Dancer {dancerNum}'s weight(kg):</strong>
                    <input type='text' onChange={weightInputHandler}></input>
                    <ReactSpeedometer
                        currentValueText="Calories/Hour"
                        value={calories}
                        maxValue={600}
                    />
                </Col>
            </Row>
        </Fragment>
    )

}

export default DancerResults;