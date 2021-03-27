import React, { useState, useEffect, Fragment } from 'react';
import { useSelector, useDispatch } from "react-redux";
import { Container, Row, Col } from "react-bootstrap";
import { Card } from './Card';
import ReactImageTooltip from 'react-image-tooltip'
import {
    legendSales,
} from "../component_variables/Variables";
import { ACCELERATIONV1GRAPH, ROLLGRAPH, TIMETAKENGRAPH, ACCURACYGRAPH, WINDOWS_DANCEMOVE, PUSHBACK_DANCEMOVE, ROCKET_DANCEMOVE, ELBOW_LOCK_DANCEMOVE, HAIR_DANCEMOVE, SCARECROW_DANCEMOVE, ZIGZAG_DANCEMOVE, SHOULDER_SHRUG_DANCEMOVE, TOTAL_MOVEMENT_DATA, TOTAL_DANCE_COUNT, ROLL, PITCH, YAW, ACCELERATION1, ACCELERATIONY, ACCELERATIONZ, MOVEMENTGRAPH, TOTALDANCEGRAPH } from './Constants';
import { GraphTabs } from './GraphTabs';
import { getUserStats } from '../actions/Statistics';
import ChartistGraph from "react-chartist";
import Faq from 'react-faq-component';
import Loader from 'react-loader-spinner'
import rollGif from '../assets/img/rollGif.gif';
import pitchGif from '../assets/img/pitchGif.gif';
import yawGif from '../assets/img/yawGif.gif';

const styles = {
    // bgColor: 'white',
    titleTextColor: "cadetblue",
    rowTitleColor: "cadetblue",
    // rowContentColor: 'grey',
    // arrowColor: "red",
};

const config = {
    animate: true,
    arrowIcon: "V",
    tabFocus: true
};
export const DetailedProgress = () => {
    const createLegend = (json) => {
        var legend = [];
        for (var i = 0; i < json["names"].length; i++) {
            var type = "fa fa-circle text-" + json["types"][i];
            legend.push(<i className={type} key={i} />);
            legend.push(" ");
            legend.push(json["names"][i]);
        }
        return legend;
    }
    var legendVelocityAcceleration = {
        names: ["Correct Moves", "Wrong moves"],
        types: ["info", "danger"]
    };

    const dispatch = useDispatch();
    // user data to be put into graph
    const { userStatistics } = useSelector((state) => state.Statistics);
    const [danceMovesData, setDanceMovesData] = useState({ WINDOWS: [], PUSHBACK: [], ROCKET: [], ELBOW_LOCK: [], HAIR: [], SCARECROW: [], ZIGZAG: [], SHOULDER_SHRUG: [] });
    const username = useSelector(state => state.Auth.user);

    const [analysisAccuracy, setAnalysisAccuracy] = useState({})
    const [analysisMovement, setAnalysisMovement] = useState({})
    const [analysisDanceCount, setAnalysisDanceCount] = useState({})

    const getDanceMoveData = () => {
        if (userStatistics === null) {
            return;
        }
        var auxState = { WINDOWS: [], PUSHBACK: [], ROCKET: [], ELBOW_LOCK: [], HAIR: [], SCARECROW: [], ZIGZAG: [], SHOULDER_SHRUG: [] };
        for (var i = 0; i < userStatistics.length; i++) {
            if (userStatistics[i].DanceMove === WINDOWS_DANCEMOVE) {
                auxState[WINDOWS_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === PUSHBACK_DANCEMOVE) {
                auxState[PUSHBACK_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === ROCKET_DANCEMOVE) {
                auxState[ROCKET_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === ELBOW_LOCK_DANCEMOVE) {
                auxState[ELBOW_LOCK_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === HAIR_DANCEMOVE) {
                auxState[HAIR_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === SCARECROW_DANCEMOVE) {
                auxState[SCARECROW_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === ZIGZAG_DANCEMOVE) {
                auxState[ZIGZAG_DANCEMOVE].push(userStatistics[i]);
            } else if (userStatistics[i].DanceMove === SHOULDER_SHRUG_DANCEMOVE) {
                auxState[SHOULDER_SHRUG_DANCEMOVE].push(userStatistics[i]);
            }
        }
        setDanceMovesData(auxState);
    }

    const getImprovementOfDances = (danceMove, danceMovesData) => {
        var danceMoveData = danceMovesData[danceMove];
        var earliestMonth = 12;
        var latestMonth = 0;
        for (var i = 0; i < danceMoveData.length; i++) {
            var monthOfData = new Date(danceMoveData[i].createdAt).getMonth();
            earliestMonth = earliestMonth > monthOfData ? monthOfData : earliestMonth;
            latestMonth = latestMonth < monthOfData ? monthOfData : latestMonth;
        }
        var earliestMonthCorrectDances = 0;
        var earliestMonthTotalDances = 0;
        var latestMonthCorrectDances = 0;
        var latestMonthTotalDances = 0;
        for (var i = 0; i < danceMoveData.length; i++) {
            var currentDataMonth = new Date(danceMoveData[i].createdAt).getMonth();
            if (currentDataMonth === earliestMonth) {
                earliestMonthTotalDances += 1;
                earliestMonthCorrectDances += danceMoveData[i].DanceMovePrediction ? 1 : 0;
            }
            if (currentDataMonth === latestMonth) {
                latestMonthTotalDances += 1;
                latestMonthCorrectDances += danceMoveData[i].DanceMovePrediction ? 1 : 0;
            }
        }
        var accuracyImprovement = latestMonthCorrectDances / latestMonthTotalDances - earliestMonthCorrectDances / earliestMonthTotalDances;
        return accuracyImprovement.toFixed(2);
    }
    const getAverageAccuracyOfDances = (danceMove, danceMovesData) => {
        var danceMoveData = danceMovesData[danceMove];
        var correctDances = 0;
        for (var i = 0; i < danceMoveData.length; i++) {
            correctDances += danceMoveData[i].DanceMovePrediction ? 1 : 0;
        }
        return (correctDances / danceMoveData.length).toFixed(2);
    }
    const getMovementDiff = (danceMove, movementType) => {
        var danceMoveData = danceMovesData[danceMove];
        var totalCorrectDances = 0;
        var totalWrongDances = 0;
        var totalCorrectDiff = 0;
        var totalWrongDiff = 0;
        for (var i = 0; i < danceMoveData.length; i++) {
            if (movementType === "roll") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AverageRoll);
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AverageRoll)
                }
            } else if (movementType === "pitch") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AveragePitch);
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AveragePitch)
                }
            } else if (movementType === "yaw") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AverageYaw);
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AverageYaw)
                }
            } else if (movementType === "accelerationX") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AverageA1)
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AverageA1)
                }
            } else if (movementType === "accelerationY") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AverageA2)
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AverageA2) 
                }
            } else if (movementType === "accelerationZ") {
                if (danceMoveData[i].DanceMovePrediction) {
                    totalCorrectDances += 1;
                    totalCorrectDiff += Math.abs(danceMoveData[i].AverageA3)
                } else {
                    totalWrongDances += 1;
                    totalWrongDiff += Math.abs(danceMoveData[i].AverageA3)
                }
            }
        }

        return (totalCorrectDiff / totalCorrectDances - totalWrongDiff / totalWrongDances).toFixed(2);
    }

    const getDanceCount = (danceMove) => {
        var danceMoveData = danceMovesData[danceMove];
        return danceMoveData.length;
    }

    const getAnalysisDescription = () => {
        var improvementOfDances = {}; // improvement of each dances {DANCE1: 5.2%, DANCE2: 6.2%....}
        var averageAccuracyOfDances = {}; // same format, as improvementOfDances
        var highestAccuracyDance = []; // index 0: dance move, index 1: accuracy
        var lowestAccuracyDance = []; // index 0 dance move, index 1 accuracy
        for (var danceMove in danceMovesData) {
            if (danceMovesData.hasOwnProperty(danceMove)) {
                improvementOfDances[danceMove] = getImprovementOfDances(danceMove, danceMovesData);
                averageAccuracyOfDances[danceMove] = getAverageAccuracyOfDances(danceMove, danceMovesData);
            }
        }
        var sortable1 = [];
        for (var danceMove in averageAccuracyOfDances) {
            sortable1.push([danceMove, averageAccuracyOfDances[danceMove]]);
        }

        sortable1.sort(function (a, b) {
            return a[1] - b[1];
        });
        if (sortable1.length > 0) {
            highestAccuracyDance = sortable1[sortable1.length - 1];
            lowestAccuracyDance = sortable1[0];
        }

        var sortable2 = [];
        for (var danceMove in improvementOfDances) {
            sortable2.push([danceMove, improvementOfDances[danceMove]]);
        }

        sortable2.sort(function (a, b) {
            return a[1] - b[1];
        });
        var lowestImprovement = sortable2.length > 0 ? sortable2[0] : null; // index 0 is dance move, index 1 is improvement made
        var highestImprovement = sortable2.length > 0 ? sortable2[sortable2.length - 1] : null; // index 0 dance move, index 1 improvement made

        var accStatSummary1 = "Your most improved dance move is " + highestImprovement[0] + ", with an average improvement of " + highestImprovement[1] + "% since you first started using this platform till now." +
            " On retrospect, your dance move " + lowestImprovement[0] + " has the lowest improvement, with a " +
            lowestImprovement[1] + "% since you first joined us.";
        var averageAccuracyOfDanceStringFormat = "";
        for (danceMove in averageAccuracyOfDances) {
            averageAccuracyOfDanceStringFormat += danceMove + ": " + averageAccuracyOfDances[danceMove] + "%, ";
        }
        var accStatSummary2 = "\nHere's an average of how you fared for each of your dances: " + averageAccuracyOfDanceStringFormat + ". We see that your highest accuracy dance is " + highestAccuracyDance[0] +
            ", good job! Your lowest accuracy dance move is " + lowestAccuracyDance[0];

        var accSuggestionSummary = "Please remember to practice more of the " + lowestAccuracyDance[0] + " dance move by going to our practice mode since it is one of your weaker dances!";
        var dataAcc = {
            title: "Insights for dance accuracies",
            rows: [
                {
                    title: "Statistical Summary",
                    content: accStatSummary1 + accStatSummary2,
                },
                {
                    title: "Suggestions to improve",
                    content: accSuggestionSummary,
                },
            ],
        };

        var totalRollDiff = {}; // speed difference between correct and wrong move of each dance move. {DANCEMOVE1: rollDiff, DANCEMOVE2: rollDiff}
        var totalPitchDiff = {}; // speed difference between correct and wrong move of each dance move. {DANCEMOVE1: pitchDiff, DANCEMOVE2: pitchDiff}
        var totalYawDiff = {}; // speed difference between correct and wrong move of each dance move. {DANCEMOVE1: yawDiff, DANCEMOVE2: yawDiff}
        // diff = correct value - wrong value
        var totalAccelerationXDiff = {}; // acceleration between correct and wrong move
        var totalAccelerationYDiff = {}; // acceleration between correct and wrong move
        var totalAccelerationZDiff = {}; // acceleration between correct and wrong move
        for (danceMove in danceMovesData) {
            if (danceMovesData.hasOwnProperty(danceMove)) {
                totalRollDiff[danceMove] = getMovementDiff(danceMove, "roll");
                totalPitchDiff[danceMove] = getMovementDiff(danceMove, "pitch");
                totalYawDiff[danceMove] = getMovementDiff(danceMove, "yaw");
                totalAccelerationXDiff[danceMove] = getMovementDiff(danceMove, "accelerationX");
                totalAccelerationYDiff[danceMove] = getMovementDiff(danceMove, "accelerationY");
                totalAccelerationZDiff[danceMove] = getMovementDiff(danceMove, "accelerationZ");
            }
        }

        var sortable3 = [];
        for (var danceMove in totalRollDiff) {
            sortable3.push([danceMove, totalRollDiff[danceMove]]);
        }
        sortable3.sort(function (a, b) {
            return a[1] - b[1];
        });
        var highestRollDiff = sortable3.length > 0 ? sortable3[0] : [NaN, NaN]; // dance move, highest diff
        sortable3 = [];
        for (var danceMove in totalPitchDiff) {
            sortable3.push([danceMove, totalPitchDiff[danceMove]]);
        }
        sortable3.sort(function (a, b) {
            return a[1] - b[1];
        });
        var highestPitchDiff = sortable3.length > 0 ? sortable3[0] : [NaN, NaN]; // dance move, highest diff
        console.log("highestPitchDiff", sortable3);
        sortable3 = [];
        for (var danceMove in totalYawDiff) {
            sortable3.push([danceMove, totalYawDiff[danceMove]]);
        }
        sortable3.sort(function (a, b) {
            return a[1] - b[1];
        });
        var highestYawDiff = sortable3.length > 0 ? sortable3[0] : [NaN, NaN]; // dance move, highest diff

        var positiveAccelerationXDiffDance = [];
        var positiveAccelerationYDiffDance = [];
        var positiveAccelerationZDiffDance = [];
        var positiveRollDiffDance = [];
        var positivePitchDiffDance = [];
        var positiveYawDiffDance = [];

        // if threshold of differences is more than 0, it will be suggested to user as movement too jerky for acceleration or slow down on roll/pitch/yaw movements
        for (danceMove in totalPitchDiff) {
            if (totalPitchDiff.hasOwnProperty(danceMove)) {
                if (totalRollDiff[danceMove] > 0) {
                    positiveRollDiffDance.push(danceMove);
                }
                if (totalPitchDiff[danceMove] > 0) {
                    positivePitchDiffDance.push(danceMove);
                }
                if (totalYawDiff[danceMove] > 0) {
                    positiveYawDiffDance.push(danceMove);
                }
                if (totalAccelerationXDiff[danceMove] > 0) {
                    positiveAccelerationXDiffDance.push(danceMove);
                }
                if (totalAccelerationYDiff[danceMove] > 0) {
                    positiveAccelerationYDiffDance.push(danceMove);
                }
                if (totalAccelerationZDiff[danceMove] > 0) {
                    positiveAccelerationZDiffDance.push(danceMove);
                }
            }
        }
        var movementStatSummary = "These are the most distinct movement differences between your CORRECT and WRONG dance moves. " + 
                                    "For ROLL movement, the " + highestRollDiff[0] + " dance move has a " + highestRollDiff[1] + 
                                    " degree/s difference. For PITCH movement, the " + highestPitchDiff[0] + " dance move has a " + highestPitchDiff[1] +
                                    " degree/s difference. For YAW movement, the " + highestYawDiff[0] + " dance move has a " + highestYawDiff[1] + " degree/s difference.\n"
        var movementSuggestionSummary = "According to the acceleration analysis, try to reduce jerky movements in the X axis for the following: " + positiveAccelerationXDiffDance + 
                                        " Try to reduce jerky movements in the Y axis for the following: " + positiveAccelerationYDiffDance + 
                                        " Try to reduce jerky movements in the Z axis for the following: " + positiveAccelerationZDiffDance;
        var movementData = {
            title: "Insights for dancer's movement",
            rows: [
                {
                    title: "Statistical Summary",
                    content: movementStatSummary,
                },
                {
                    title: "Suggestions to improve",
                    content: movementSuggestionSummary,
                },
            ],
        };

        var danceCounts = {}; // dance counts for each dance move
        for (danceMove in danceMovesData) {
            danceCounts[danceMove] = getDanceCount(danceMove);
        }

        var sortable3 = [];
        for (var danceMove in danceCounts) {
            sortable3.push([danceMove, danceCounts[danceMove]]);
        }

        sortable3.sort(function (a, b) {
            return a[1] - b[1];
        });
        var lowestDanceCount = sortable3.length > 0 ? sortable3[0] : null;
        var highestDanceCount = sortable3.length > 0 ? sortable3[sortable3.length - 1] : null;

        var danceCountStatSummary = "You danced " + highestDanceCount[0] + " " + highestDanceCount[1] + " number of times, the highest among your dances, well done! On the other hand, " +
            "you danced " + lowestDanceCount[0] + " " + lowestDanceCount[1] + "number of times, which is the least among all the dances, maybe try pay more attention to " + lowestDanceCount[0] + "!";


        var danceCountData = {
            title: "Insights for dance count",
            rows: [
                {
                    title: "Statistical Summary",
                    content: danceCountStatSummary,
                },
            ],
        };
        setAnalysisAccuracy(dataAcc);
        setAnalysisMovement(movementData);
        setAnalysisDanceCount(danceCountData);
        return;
    }

    useEffect(() => {
        dispatch(getUserStats(username));
    }, [])

    useEffect(() => {
        getDanceMoveData();
        getAnalysisDescription();
    }, [userStatistics])

    const getDanceMovesCount = () => {
        var danceMovesArr = new Array(TOTAL_DANCE_COUNT).fill(0);
        var dances = Object.keys(danceMovesData);
        for (var i = 0; i < danceMovesArr.length; i++) {
            danceMovesArr[i] = danceMovesData[dances[i]].length;
        }
        return { labels: dances, series: [danceMovesArr] };
    }


    return (
        <div className="content">
            {userStatistics === null ?
                <Container>
                    <Loader
                        type="Bars"
                        color="#00BFFF"
                        height={100}
                        width={100}
                    />
                    <h3>Please wait.. </h3> <br/>
                    <p>If you have not dance yet, please head over to practice mode for us to analyse your dances!</p>
                </Container>
                :
                <Container fluid style={{ paddingTop: "10px" }}>
                    <Row>
                        <Col md={8}>
                            <Card
                                id="chartTimeseries"
                                title="Accuracy of each dance moves"
                                content={
                                    <GraphTabs
                                        graphType={ACCURACYGRAPH}
                                        danceMovesData={danceMovesData}
                                    />
                                }
                            />
                        </Col>
                        <Col md={4}>
                            <Faq data={analysisAccuracy} styles={styles} config={config} />
                        </Col>
                    </Row>
                    <Col>
                    </Col>
                    <Row>
                        <Col md={8}>
                            <Card
                                id="chartTimeseries"
                                title="Absolute roll, pitch, yaw (degree/s) and acceleration (degree^2/s)"
                                content={
                                    <GraphTabs
                                        graphType={MOVEMENTGRAPH}
                                        danceMovesData={danceMovesData}
                                    />
                                }
                                legend={
                                    <div className="legend">{createLegend(legendVelocityAcceleration)}</div>
                                }
                            />
                        </Col>
                        <Col md={4}>
                            <Faq data={analysisMovement} styles={styles} config={config} />
                            <ReactImageTooltip image={rollGif}>
                                <a href="">
                                    Hover to see what ROLL looks like!
                                </a>
                            </ReactImageTooltip> <br />
                            <ReactImageTooltip image={pitchGif}>
                                <a href="">
                                    Hover to see what PITCH looks like!
                                </a>
                            </ReactImageTooltip> <br />
                            <ReactImageTooltip image={yawGif}>
                                <a href="">
                                    Hover to see what YAW looks like!
                                </a>
                            </ReactImageTooltip>
                        </Col>
                    </Row>
                    <Row>
                        <Col md={8}>
                            <Card
                                id="chartTimeseries"
                                title="Dance count for each dances"
                                content={
                                    <ChartistGraph
                                        data={getDanceMovesCount()}
                                        type="Bar"
                                    />
                                }
                            />
                        </Col>
                        <Col md={4}>
                            <Faq data={analysisDanceCount} styles={styles} config={config} />
                        </Col>
                    </Row>
                </Container>
            }
        </div>
    )
}