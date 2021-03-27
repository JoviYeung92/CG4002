import RangeSlider from 'react-bootstrap-range-slider';
import React, { useState, Fragment, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { pushUserStats } from '../actions/Statistics';
import { CORRECT, ELBOW_LOCK_DANCEMOVE, HAIR_DANCEMOVE, WAITING, PUSHBACK_DANCEMOVE, ROCKET_DANCEMOVE, SCARECROW_DANCEMOVE, SHOULDER_SHRUG_DANCEMOVE, WINDOWS_DANCEMOVE, WRONG, ZIGZAG_DANCEMOVE } from './Constants';
import { Container, Row, Col } from "react-bootstrap";
import Zoom from 'react-reveal/Zoom';
import elbowlock from '../assets/img/dances/elbowlock.gif';
import hair from '../assets/img/dances/hair.gif';
import pushback from '../assets/img/dances/pushback.gif';
import rocket from '../assets/img/dances/rocket.gif';
import scarecrow from '../assets/img/dances/scarecrow.gif';
import shouldershrug from '../assets/img/dances/shouldershrug.gif';
import windows from '../assets/img/dances/windows.gif';
import zigzag from '../assets/img/dances/zigzag.gif';

const gifToString = (gif) => {
    if (gif === null) {
        return null;
    }
    if (gif === elbowlock) {
        return ELBOW_LOCK_DANCEMOVE;
    } else if (gif === hair) {
        return HAIR_DANCEMOVE;
    } else if (gif === pushback) {
        return PUSHBACK_DANCEMOVE
    } else if (gif === rocket) {
        return ROCKET_DANCEMOVE;
    } else if (gif === scarecrow) {
        return SCARECROW_DANCEMOVE
    } else if (gif === shouldershrug) {
        return SHOULDER_SHRUG_DANCEMOVE;
    } else if (gif === windows) {
        return WINDOWS_DANCEMOVE
    } else if (gif === zigzag) {
        return ZIGZAG_DANCEMOVE;
    }
}

// configuration panel for practice timer, praise mode etc, once user press start, countdown and open 2 columns
// start tracking how much time user spent on each dance move
// to predict each dance move: samuel send me raw sensor data via database, socket it and start collecting input, send it to model script for prediction once user press start
// 2 columns view once start button is pressed, left column shows correct and wrong dance moves, right shows video gif of dance moves from luminus folder
export const PracticeMode = () => {
    const [toDanceCount, setToDanceCount] = useState(1);
    const [toPraise, setToPraise] = useState(false);
    const [hasStart, setHasStart] = useState(false);
    const [danceMoves, setDanceMoves] = useState([]);
    const danceItems = { 'elbowlock': elbowlock, 'hair': hair, 'pushback': pushback, 'rocket': rocket, 'scarecrow': scarecrow, 'shouldershrug': shouldershrug, 'windows': windows, 'zigzag': zigzag };
    const [checkboxItems, setCheckboxItems] = useState(Object.keys(danceItems));
    const [prediction, setPrediction] = useState(WAITING);
    const [userDanceMove, setUserDanceMove] = useState(null);
    var color = 'black';
    const username = useSelector(state => state.Auth.user);
    const dispatch = useDispatch();
    const getColor = () => {
        if (prediction === WRONG)
            color = 'red';
        else if (prediction === CORRECT)
            color = 'green';
        else
            color = 'black'
    }
    const setPraise = (event) => {
        setToPraise(event.target.value === "yes" ? true : false)
    }
    const handleStart = () => {
        setHasStart(true);
        var arr = [];
        var selectedDanceGif = [];
        for (var i = 0; i < checkboxItems.length; i++) {
            selectedDanceGif.push(danceItems[checkboxItems[i]]);
        }
        var index = 0;
        for (var i = 0; i < toDanceCount; i++) {
            index += 1;
            index = index >= selectedDanceGif.length ? 0 : index;
            arr.push(selectedDanceGif[index]);
        }
        setDanceMoves(arr);
    }
    const handleRestart = () => {
        setHasStart(false);
        setDanceMoves([]);
        setCheckboxItems(Object.keys(danceItems));
        setPrediction(WAITING);
        setUserDanceMove(null);
    }
    const handleSkip = () => {
        setDanceMoves(danceMoves.filter((_, i) => i !== 0));
        setPrediction(WAITING);
    }
    const handleCheckboxChange = (e) => {
        const dance = e.target.name;
        if (e.target.checked) {
            setCheckboxItems([
                ...checkboxItems,
                dance
            ])
        } else {
            const updated = checkboxItems.filter(i => i !== dance);
            setCheckboxItems(updated);
        }
    }
    const checkbox = (danceMove) => {
        return (
            <label style={{ paddingRight: "20px" }} key={danceMove}>
                <input
                    type="checkbox"
                    defaultChecked={true}
                    onChange={handleCheckboxChange}
                    name={danceMove}
                />
                {danceMove}
            </label>
        )
    }
    const checkboxes = () => (
        Object.keys(danceItems).map((checkbox))
    )

    const praiseOrNot = (prediction, praise) => {
        if (praise) {
            if (prediction === CORRECT) {
                return <h2>Good job, way to go!</h2>
            } else if (prediction === WRONG) {
                return <h2>It's okay! Keep up the good effort and try again!</h2>
            }
        }
    }
    var rawSensorDatas = [];
    const collectRawSensorData = data => {
        if (hasStart) {
            const v1 = data.Roll;
            const v2 = data.Pitch;
            const v3 = data.Yaw;
            const a1 = data.GravitationalA1;
            const a2 = data.GravitationalA2;
            const a3 = data.GravitationalA3;
            const toPush = [v1, v2, v3, a1, a2, a3];
            rawSensorDatas.push(toPush);
        }
    }
    const pushStatisticsData = (predictedMove, userMove) => {
        var averageRoll = null;
        var averagePitch = null;
        var averageYaw = null;
        var averageA1 = null;
        var averageA2 = null;
        var averageA3 = null;
        var size = rawSensorDatas.length
        var danceMovePrediction = predictedMove === userMove ? true : false;
        rawSensorDatas.forEach((elem) => {
            averageRoll += elem[0];
            averagePitch += elem[1];
            averageYaw += elem[2];
            averageA1 += elem[3];
            averageA2 += elem[4];
            averageA3 += elem[5];
        })
        console.log("size", size);
        averageRoll = averageRoll / size;
        averagePitch = averagePitch / size;
        averageYaw = averageYaw / size;
        averageA1 = averageA1 / size;
        averageA2 = averageA2 / size;
        averageA3 = averageA3 / size;
        console.log('average', averageRoll);
        var formData = {
            Username: username, DanceMovePrediction: danceMovePrediction, DanceMove: userDanceMove, AverageRoll: averageRoll, AveragePitch: averagePitch, AverageYaw: averageYaw,
            AverageA1: averageA1, AverageA2: averageA2, AverageA3: averageA3
        };
        dispatch(pushUserStats(formData));
    }
    useEffect(() => {
        setUserDanceMove(gifToString(danceMoves[0]));
    }, [danceMoves])

    // Push average statistics back to DB everytime there's a new prediction, if user is not dancing, ignore the raw datas
    const getPrediction = (socket, userDanceMove, data) => {
        if (hasStart) {
            data.DanceMovePrediction === userDanceMove ? setPrediction(CORRECT) : setPrediction(WRONG);
            pushStatisticsData(data.DanceMovePrediction, userDanceMove);
            rawSensorDatas = [];
        }
    }
    const socket = useSelector((state) => state.Socket.socket)
    useEffect(() => {
        socket.off('realPrediction');
        if (socket !== null && userDanceMove != null) {
            socket.on('realPrediction', function (data) {
                getPrediction(socket, userDanceMove, data);
            });
            socket.on('realRawSensorData', collectRawSensorData);
        }
    }, [socket, userDanceMove])
    return (
        <div>
            {
                hasStart ?
                    <Container>
                        <Row>
                            {danceMoves.length > 0 ? 
                            <Col style={{ border: '2px solid #444' }}>
                                <br />
                                <button className="btn btn-info" onClick={handleSkip}>{prediction === CORRECT ? 'PROCEED' : 'SKIP'}</button>
                                <button className="btn btn-danger" onClick={handleRestart}>RESTART</button>
                                <div className="row banner">
                                    <div className="banner-text">
                                        {getColor()}
                                        {prediction === WAITING ?
                                            <h1 style={{ color: `${color}` }}>{prediction}</h1>
                                            :
                                            <Zoom duration={3000}>
                                                <h1 style={{ color: `${color}`, position: 'absolute', top: '50%', transform: 'translate(-50%, -50%)', fontSize: '100px' }}>{prediction}</h1>
                                            </Zoom>
                                        }
                                        {prediction === CORRECT ? 
                                            praiseOrNot(CORRECT, toPraise)
                                            :
                                            prediction === WRONG ? 
                                            praiseOrNot(WRONG, toPraise)
                                            :
                                            null
                                        }
                                    </div>
                                </div>
                            </Col>
                            :
                            <Col style={{ border: '2px solid #444' }}>
                                <button className="btn btn-danger" onClick={handleRestart}>RESTART</button>
                            </Col>
                            }
                            <Col>
                                <img src={danceMoves[0]} alt="FINISHED! :)" style={{ width: "500px", height: "700px" }} />
                            </Col>
                        </Row>
                    </Container>
                    :
                    <Container style={{ border: '2px solid #444' }}>
                        <h3>How many dances</h3>
                        <RangeSlider
                            value={toDanceCount}
                            onChange={changeEvent => setToDanceCount(changeEvent.target.value)}
                            min={1}
                            max={15}
                        />
                        <h3>Dances to practice</h3>
                        {checkboxes()}
                        <h3>Do you want praises?</h3>
                        <div onChange={setPraise}>
                            <input type="radio" id="yes" value="yes" name="praises" />
                            <label htmlFor="yes" style={{ paddingRight: "20px" }}>Yes</label>
                            <input type="radio" id="no" value="no" name="praises" defaultChecked="checked" />
                            <label htmlFor="no">No</label>
                        </div>
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}>
                            <button className="btn btn-success" type="submit" onClick={handleStart} style={{ fontSize: "50px" }}>START</button>
                        </div>
                    </Container>
            }
        </div>
    )
}