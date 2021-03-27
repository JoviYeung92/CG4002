import React, { useState, Fragment, useEffect } from "react";
import { Line } from "react-chartjs-2";
import 'chartjs-plugin-streaming';
import { useSelector } from "react-redux";
import { ACCELERATIONX, ACCELERATIONY, ROLL, ROLLGRAPH, PITCH, YAW, ABSOLUTE_AVG_ACCELERATION_GRAPH, PITCHGRAPH, YAWGRAPH } from "./Constants";
import { Tabs, Tab } from 'react-bootstrap';

/**
 * Sample line chart settings from http://jerairrest.github.io/react-chartjs-2/
 * @param {array<string>} labels
 * @param {array<T>} data
 * @param {string} label
 */
const lineData = (label) => {
    return {
        datasets: [
            {
                label: label,
                fillColor: 'rgba(220,220,220,0.2)',
                strokeColor: 'rgba(220,220,220,1)',
                pointColor: 'rgba(220,220,220,1)',
                pointStrokeColor: '#fff',
                pointHighlightFill: '#fff',
                pointHighlightStroke: 'rgba(220,220,220,1)',
                data: [],
            },
        ]
    }
};
var dancerOne = {
    roll: 0,
    pitch: 0,
    yaw: 0,
    accelerationX:0,
    accelerationY:0,
    accelerationZ:0,
};
var dancerTwo = {
    roll: 0,
    pitch: 0,
    yaw: 0,
    accelerationX:0,
    accelerationY:0,
    accelerationZ:0,
};
var dancerThree = {
    roll: 0,
    pitch: 0,
    yaw: 0,
    accelerationX:0,
    accelerationY:0,
    accelerationZ:0,
};

const getSensorData = (data) => {
    if (data.Dancer === 1) {
        dancerOne.roll = data.Roll;
        dancerOne.pitch = data.Pitch;
        dancerOne.yaw = data.Yaw;
        dancerOne.accelerationX = data.GravitationalA1;
        dancerOne.accelerationY = data.GravitationalA2;
        dancerOne.accelerationZ = data.GravitationalA3;
    } else if (data.Dancer === 2) {
        dancerTwo.roll = data.Roll;
        dancerTwo.pitch = data.Pitch;
        dancerTwo.yaw = data.Yaw;
        dancerTwo.accelerationX = data.GravitationalA1;
        dancerTwo.accelerationY = data.GravitationalA2;
        dancerTwo.accelerationZ = data.GravitationalA3;
    } else if (data.Dancer === 3) {
        dancerThree.roll = data.Roll;
        dancerThree.pitch = data.Pitch;
        dancerThree.yaw = data.Yaw;
        dancerThree.accelerationX = data.GravitationalA1;
        dancerThree.accelerationY = data.GravitationalA2;
        dancerThree.accelerationZ = data.GravitationalA3;
    }
}
const outputDataPoint = (dancer, graphType) => {
    var dataPoint = 0;
    if (graphType === ROLLGRAPH) {
        dataPoint = dancer === 1 ? dancerOne.roll : dancer === 2 ? dancerTwo.roll : dancer === 3 ? dancerThree.roll : 0
    } else if (graphType === PITCHGRAPH) {
        dataPoint = dancer === 1 ? dancerOne.pitch : dancer === 2 ? dancerTwo.pitch : dancer === 3 ? dancerThree.pitch : 0
    } else if (graphType === YAWGRAPH) {
        dataPoint = dancer === 1 ? dancerOne.yaw : dancer === 2 ? dancerTwo.yaw : dancer === 3 ? dancerThree.yaw : 0
    } else if (graphType === ABSOLUTE_AVG_ACCELERATION_GRAPH) {
        dataPoint = dancer === 1 ? (Math.abs(dancerOne.accelerationX)+Math.abs(dancerOne.accelerationY)+Math.abs(dancerOne.accelerationZ))/3 
                    : dancer === 2 ? (Math.abs(dancerTwo.accelerationX)+Math.abs(dancerTwo.accelerationY)+Math.abs(dancerTwo.accelerationZ))/3
                    : dancer === 3 ? (Math.abs(dancerThree.accelerationX)+Math.abs(dancerThree.accelerationY)+Math.abs(dancerThree.accelerationZ))/3
                    : 0
    }
    return dataPoint;
}
export const RealtimeLineGraph = ({ dancer, graphType }) => {
    var label = graphType;
    const socket = useSelector((state) => state.Socket.socket)

    useEffect(() => {
        if (socket !== null)
            socket.on('realRawSensorData', getSensorData);
    }, [socket])

    let data = lineData(label);
    const options = {
        scales: {
            yAxes: [
                {
                    scaleLabel: {
                        display: true,
                        labelString: "degree/s or degree/s^2",
                    },
                },
            ],
            xAxes: [
                {
                    type: 'realtime',
                    realtime: {
                        onRefresh: (data) => {
                            data.data.datasets.forEach(function (dataset) {
                                dataset.data.push({
                                    x: Date.now(),
                                    y: outputDataPoint(dancer, graphType)
                                });
                            });
                        }
                    },
                    scaleLabel: {
                        display: true,
                        labelString: "Time",
                    },
                },
            ],
        },
    };
    return (
        <Fragment>
            <Line data={data} options={options} />
        </Fragment>
    );
};