import React, { useState, Fragment } from 'react'
import { ProgressCharts } from './ProgressCharts';
import { Tabs, Tab } from 'react-bootstrap';
import { ACCURACYGRAPH, WINDOWS_DANCEMOVE, PUSHBACK_DANCEMOVE, ROCKET_DANCEMOVE, ELBOW_LOCK_DANCEMOVE, HAIR_DANCEMOVE, SCARECROW_DANCEMOVE, ZIGZAG_DANCEMOVE, SHOULDER_SHRUG_DANCEMOVE, ROLL, PITCH, YAW, ACCELERATIONX, ACCELERATIONY, ACCELERATIONZ } from './Constants';
import {
    dataBar,
    dataSales,
} from "../component_variables/Variables";

var dataAcc= {
    title: "Insights for dance accuracies",
    rows: [
        {
            title: "Statistical Summary",
            content: '',
        },
        {
            title: "Suggestions to improve",
            content: '',
        },
    ],
};
var dataMovement= {
    title: "Insights for dance movements",
    rows: [
        {
            title: "Statistical Summary",
            content: '',
        },
        {
            title: "Suggestions to improve",
            content: '',
        },
    ],
};
export const GraphTabs = ({ graphType, danceMovesData }) => {
    const [key, setKey] = useState('Windows');

    const getAccuracyData = (danceMove) => {
        const danceMoveData = danceMovesData[danceMove]; // array of dicts of a particular dance move statistics
        var numToMonth = {0: "Jan", 1: "Feb", 2: "Mar", 3: "Apr", 4: "May", 5: "Jun", 6: "Jul", 7: "Aug", 8: "Sep", 9: "Oct", 10: "Nov", 11: "Dec"};
        var correctPredictionForMonth = new Array(12).fill(null);
        var dataSizeForMonth = new Array(12).fill(null);
        if (danceMoveData === undefined) {
            return dataSales
        }
        var earliestDatetime = new Date(8640000000000000);
        var latestDatetime = new Date(-8640000000000000);
        for (var i = 0; i < danceMoveData.length; i++) {
            var resultDatetime = new Date(danceMoveData[i].createdAt);
            var month = resultDatetime.getMonth()
            dataSizeForMonth[month] += 1;
            correctPredictionForMonth[month] += danceMoveData[i].DanceMovePrediction ? 1 : 0;
            earliestDatetime = earliestDatetime > resultDatetime ? resultDatetime : earliestDatetime;
            latestDatetime = latestDatetime < resultDatetime ? resultDatetime : latestDatetime;
        }
        var earliestMonthNum = earliestDatetime.getMonth();
        var latestMonthNum = latestDatetime.getMonth();
        for (var i = 0; i < 12; i++) {
            correctPredictionForMonth[i] = dataSizeForMonth[i] === 0 ? null : correctPredictionForMonth[i] / dataSizeForMonth[i];
        }
        var labels = [];
        var series = [];
        for (var i=earliestMonthNum; i<=latestMonthNum; i++) {
            labels.push(numToMonth[i]);
            series.push(correctPredictionForMonth[i]);
        }
        const graphData = { labels: labels, series: [series] };
        return graphData;
    }

    const getMovementData = (danceMove) => {
        const danceMoveData = danceMovesData[danceMove]; // array of dicts of particular dance move statistics
        var correctData = { ROLL: 0.0, PITCH: 0.0, YAW: 0.0, ACCELERATIONX: 0.0, ACCELERATIONY: 0.0, ACCELERATIONZ: 0.0 };
        var wrongData = { ROLL: 0.0, PITCH: 0.0, YAW: 0.0, ACCELERATIONX: 0.0, ACCELERATIONY: 0.0, ACCELERATIONZ: 0.0 };
        var correctCount = 0;
        if (danceMoveData === undefined) {
            return dataBar
        }
        for (var i = 0; i < danceMoveData.length; i++) {
            var prediction = danceMoveData[i].DanceMovePrediction;
            if (prediction) {
                correctCount += 1;
                correctData[ROLL] += Math.abs(danceMoveData[i].AverageRoll);
                correctData[PITCH] += Math.abs(danceMoveData[i].AveragePitch);
                correctData[YAW] += Math.abs(danceMoveData[i].AverageYaw);
                correctData[ACCELERATIONX] += Math.abs(danceMoveData[i].AverageA1);
                correctData[ACCELERATIONY] += Math.abs(danceMoveData[i].AverageA2);
                correctData[ACCELERATIONZ] += Math.abs(danceMoveData[i].AverageA3);
            } else {
                wrongData[ROLL] += Math.abs(danceMoveData[i].AverageRoll);
                wrongData[PITCH] += Math.abs(danceMoveData[i].AveragePitch);
                wrongData[YAW] += Math.abs(danceMoveData[i].AverageYaw);
                wrongData[ACCELERATIONX] += Math.abs(danceMoveData[i].AverageA1);
                wrongData[ACCELERATIONY] += Math.abs(danceMoveData[i].AverageA2);
                wrongData[ACCELERATIONZ] += Math.abs(danceMoveData[i].AverageA3);
            }
        }
        correctData[ROLL] /= correctCount;
        correctData[PITCH] /= correctCount;
        correctData[YAW] /= correctCount;
        correctData[ACCELERATIONX] /= correctCount;
        correctData[ACCELERATIONY] /= correctCount;
        correctData[ACCELERATIONZ] /= correctCount;
        var wrongCount = danceMoveData.length - correctCount;
        wrongData[ROLL] /= wrongCount;
        wrongData[PITCH] /= wrongCount;
        wrongData[YAW] /= wrongCount;
        wrongData[ACCELERATIONX] /= wrongCount;
        wrongData[ACCELERATIONY] /= wrongCount;
        wrongData[ACCELERATIONZ] /= wrongCount;

        var label = Object.keys(correctData);
        var seriesCorrect = Object.values(correctData);
        var seriesWrong = Object.values(wrongData);
        const graphData = { labels: label, series: [seriesCorrect, seriesWrong] };
        return graphData;
    }

    return (
        /*
            data is either for accuracy graph or movement graph
        */
            <Tabs
                id="controlled-tab-example"
                activeKey={key}
                onSelect={(k) => setKey(k)}
            >
                <Tab eventKey="Windows" title="Windows">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(WINDOWS_DANCEMOVE) : getMovementData(WINDOWS_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="Pushback" title="Pushback">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(PUSHBACK_DANCEMOVE) : getMovementData(PUSHBACK_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="Rocket" title="Rocket">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(ROCKET_DANCEMOVE) : getMovementData(ROCKET_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="ElbowLock" title="ElbowLock">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(ELBOW_LOCK_DANCEMOVE) : getMovementData(ELBOW_LOCK_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="Hair" title="Hair">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(HAIR_DANCEMOVE) : getMovementData(HAIR_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="Scarecrow" title="Scarecrow">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(SCARECROW_DANCEMOVE) : getMovementData(SCARECROW_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="ZigZag" title="ZigZag">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(ZIGZAG_DANCEMOVE) : getMovementData(ZIGZAG_DANCEMOVE)}
                    />
                </Tab>
                <Tab eventKey="ShoulderShrug" title="ShoulderShrug">
                    <ProgressCharts
                        graphType={graphType}
                        data={graphType === ACCURACYGRAPH ? getAccuracyData(SHOULDER_SHRUG_DANCEMOVE) : getMovementData(SHOULDER_SHRUG_DANCEMOVE)}
                    />
                </Tab>
            </Tabs>
    )
}