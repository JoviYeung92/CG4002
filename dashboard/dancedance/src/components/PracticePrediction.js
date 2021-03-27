// import React, { useState, Fragment, useEffect } from 'react';
// import { useSelector, useDispatch } from 'react-redux';
// import { pushUserStats } from '../actions/Statistics';
// import { CORRECT, ELBOW_LOCK_DANCEMOVE, HAIR_DANCEMOVE, WAITING, PUSHBACK_DANCEMOVE, ROCKET_DANCEMOVE, SCARECROW_DANCEMOVE, SHOULDER_SHRUG_DANCEMOVE, WINDOWS_DANCEMOVE, WRONG, ZIGZAG_DANCEMOVE } from './Constants';
// import Zoom from 'react-reveal/Zoom';
// import elbowlock from '../assets/img/dances/elbowlock.gif';
// import hair from '../assets/img/dances/hair.gif';
// import pushback from '../assets/img/dances/pushback.gif';
// import rocket from '../assets/img/dances/rocket.gif';
// import scarecrow from '../assets/img/dances/scarecrow.gif';
// import shouldershrug from '../assets/img/dances/shouldershrug.gif';
// import windows from '../assets/img/dances/windows.gif';
// import zigzag from '../assets/img/dances/zigzag.gif';

// // userDanceMove is the dance move gif appearing on dashboard
// export const PracticePrediction = ({ danceMoveGif, index}) => {
//     const userDanceMove = gifToString(danceMoveGif);
//     const [prediction, setPrediction] = useState(WAITING);
//     var color = 'black';
//     const username = useSelector(state => state.Auth.user);
//     const dispatch = useDispatch();
//     const getColor = () => {
//         if (prediction === WRONG)
//             color = 'red';
//         else if (prediction === CORRECT)
//             color = 'green';
//         else
//             color = 'black'
//     }
//     var rawSensorDatas = [];
//     const collectRawSensorData = data => {
//         const v1 = data.RotationalV1;
//         const v2 = data.RotationalV2;
//         const v3 = data.RotationalV3;
//         const a1 = data.GravitationalA1;
//         const a2 = data.GravitationalA2;
//         const a3 = data.GravitationalA3;
//         rawSensorDatas.push([v1, v2, v3, a1, a2, a3]);
//     }
//     const pushStatisticsData = () => {
//         if (prediction !== WAITING) {
//             var averageV1 = null;
//             var averageV2 = null;
//             var averageV3 = null;
//             var averageA1 = null;
//             var averageA2 = null;
//             var averageA3 = null;
//             var size = rawSensorDatas.length
//             for (var i = 0; i < size; i++) {
//                 averageV1 += rawSensorDatas[i][0];
//                 averageV2 += rawSensorDatas[i][1];
//                 averageV3 += rawSensorDatas[i][2];
//                 averageA1 += rawSensorDatas[i][3];
//                 averageA2 += rawSensorDatas[i][4];
//                 averageA3 += rawSensorDatas[i][5];
//             }
//             averageV1 = averageV1 / size;
//             averageV2 = averageV2 / size;
//             averageV3 = averageV3 / size;
//             averageA1 = averageA1 / size;
//             averageA2 = averageA2 / size;
//             averageA3 = averageA3 / size;
//             rawSensorDatas = [];
//             const mySqlDatetime = new Date().toISOString().slice(0, 19).replace('T', ' ');
//             var formData = {
//                 Username: username, DanceMovePrediction: null, DanceMove: userDanceMove, AverageV1: averageV1, AverageV2: averageV2, AverageV3: averageV3,
//                 AverageA1: averageA1, AverageA2: averageA2, AverageA3: averageA3, createdAt: mySqlDatetime, updatedAt: mySqlDatetime
//             };
//             if (prediction === WRONG) {
//                 formData.DanceMovePrediction = false;
//             } else if (prediction === CORRECT) {
//                 formData.DanceMovePrediction = true;
//             }
//             dispatch(pushUserStats(formData));
//         }
//     }
//     // Push average statistics back to DB everytime there's a new prediction, if user is not dancing, ignore the raw datas
//     const getPrediction = data => {
//         console.log(data)
//         if (data.DanceMovePrediction !== userDanceMove) {
//             setPrediction(WRONG);
//         } else {
//             setPrediction(CORRECT);
//         }
//         pushStatisticsData();
//     }
//     const socket = useSelector((state) => state.Socket.socket)
//     useEffect(() => {
//         if (socket !== null) {
//             socket.on('realPrediction', getPrediction);
//             socket.on('realRawSensorData', collectRawSensorData);
//         }
//     }, [socket])

//     return (
//         <Fragment>
//             <div className="row banner">
//                 <div className="banner-text">
//                     {getColor()}
//                     {prediction === WAITING ?
//                         <h1 style={{ color: `${color}` }}>{prediction}</h1>
//                         :
//                         <Zoom duration={3000}>
//                             <h1 style={{ color: `${color}`, position: 'absolute', top: '50%', transform: 'translate(-50%, -50%)', fontSize:'100px'}}>{prediction}</h1>
//                         </Zoom>
//                     }
//                 </div>
//             </div>
//         </Fragment>

//     )
// }