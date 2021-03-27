import React, { useState, Fragment, useEffect } from "react";
import { Doughnut, Bar } from 'react-chartjs-2';
import { useSelector } from "react-redux";

const dummydata = {
    datasets: [{
        backgroundColor: ['red', 'green', 'blue', 'orange', 'yellow', 'purple', 'cyan', 'brown', 'silver', 'magenta'],
        data: [10, 20, 30, 12, 12, 23, 34]
    }],

    // These labels appear in the legend and in the tooltips when hovering different arcs
    labels: [
        'Red',
        'Yellow',
        'Blue'
    ]
};

var predictedDances1 = {

};
var predictedDances2 = {

};
var predictedDances3 = {

};

const getSensorData = (data) => {
    if (data.DancerNumber === 1) {
        if (predictedDances1.hasOwnProperty(data.DanceMovePrediction)) {
            predictedDances1 = {
                ...predictedDances1,
                [data.DanceMovePrediction]: predictedDances1[data.DanceMovePrediction] + 1
            }
        } else {
            predictedDances1 = {
                ...predictedDances1,
                [data.DanceMovePrediction]: 0
            }
        }
    } else if (data.DancerNumber === 2) {
        if (predictedDances2.hasOwnProperty(data.DanceMovePrediction)) {
            predictedDances2 = {
                ...predictedDances2,
                [data.DanceMovePrediction]: predictedDances2[data.DanceMovePrediction] + 1
            }
        } else {
            predictedDances2 = {
                ...predictedDances2,
                [data.DanceMovePrediction]: 0
            }
        }
    } else if (data.DancerNumber === 3) {
        if (predictedDances3.hasOwnProperty(data.DanceMovePrediction)) {
            predictedDances3 = {
                ...predictedDances3,
                [data.DanceMovePrediction]: predictedDances3[data.DanceMovePrediction] + 1
            }
        } else {
            predictedDances3 = {
                ...predictedDances3,
                [data.DanceMovePrediction]: 0
            }
        }
    }
}
const graphData = (dancer) => {
    var backgroundColor = ['red', 'green', 'blue', 'orange', 'yellow', 'purple', 'cyan', 'brown', 'silver', 'magenta'];
    var labels = [];
    var predictedDances = {};
    var data = [];
    if (dancer === 1) {
        predictedDances = predictedDances1;
    } else if (dancer === 2) {
        predictedDances = predictedDances2;
    } else if (dancer === 3) {
        predictedDances = predictedDances3;
    }
    for (var key in predictedDances) {
        labels.push(key);
        data.push(predictedDances[key]);
    }
    console.log("TEST", dancer, predictedDances);
    return { datasets: [{ data: data, backgroundColor: backgroundColor }], labels: labels };
}
export const EvalMiniPredictiongraph = ({ dancer }) => {
    const socket = useSelector((state) => state.Socket.socket)


    useEffect(() => {
        if (socket !== null)
            socket.on('realPrediction', getSensorData);
    }, [socket]);

    return (
        <Doughnut data={graphData(dancer)} />
    )
}