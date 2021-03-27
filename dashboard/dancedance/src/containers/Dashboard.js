import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from "react-redux"
import ChartistGraph from "react-chartist";
import { Container, Row, Col } from "react-bootstrap";
import { Card } from '../components/Card';
import { StatsCard } from '../components/StatsCard';
import {
    dataPie,
    legendPie,
    dataSales,
    optionsSales,
    responsiveSales,
    legendSales,
} from "../component_variables/Variables";
import { getUserStats } from '../actions/Statistics';
import Loader from 'react-loader-spinner'


export const Dashboard = () => {
    const username = useSelector(state => state.Auth.user);
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

    const dispatch = useDispatch();
    useEffect(() => {
        dispatch(getUserStats(username));
    }, [])
    // user data to be put into graph
    const { userStatistics } = useSelector((state) => state.Statistics);
    const totalDances = userStatistics !== null ? userStatistics.length : 0;
    var options = {
        low: 0,
        high: totalDances,
        showArea: false,
        height: "245px",
        axisX: {
            showGrid: false
        },
        lineSmooth: true,
        showLine: true,
        showPoint: true,
        fullWidth: true,
        chartPadding: {
            right: 50
        }
    };
    const danceAccuracy = () => {
        if (userStatistics === null) {
            return;
        }
        const correctMoves = userStatistics.filter((stat) => stat.DanceMovePrediction === true);
        const correctMovesPercent = Math.floor((correctMoves.length / totalDances) * 100);
        console.log(correctMovesPercent)
        const dataPie = {
            labels: [`${correctMovesPercent}%`, `${100 - correctMovesPercent}%`],
            series: [correctMovesPercent, 100 - correctMovesPercent]
        };
        return dataPie;
    }

    const totalDancesGraph = () => {
        if (userStatistics === null) {
            return;
        }
        var earliestDatetime = new Date(8640000000000000);
        var latestDatetime = new Date(-8640000000000000);
        var numToMonth = { 0: "Jan", 1: "Feb", 2: "Mar", 3: "Apr", 4: "May", 5: "Jun", 6: "Jul", 7: "Aug", 8: "Sep", 9: "Oct", 10: "Nov", 11: "Dec" };
        var dancesForEachMonth = { 0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0 };
        for (var i = 0; i < userStatistics.length; i++) {
            const t = userStatistics[i].createdAt.split(/[- :]/);
            var resultDatetime = new Date(userStatistics[i].createdAt);
            earliestDatetime = earliestDatetime > resultDatetime ? resultDatetime : earliestDatetime;
            latestDatetime = latestDatetime < resultDatetime ? resultDatetime : latestDatetime;
            dancesForEachMonth[resultDatetime.getMonth()] += 1;
        }
        var earliestMonthNum = earliestDatetime.getMonth();
        var latestMonthNum = latestDatetime.getMonth();
        var labels = [];
        var series = [];
        var totalDances = 0;
        for (var i = earliestMonthNum; i <= latestMonthNum; i++) {
            labels.push(numToMonth[i]);
            totalDances += dancesForEachMonth[i];
            series.push(totalDances);
        }
        const graphData = { labels: labels, series: [series] };
        return graphData;

    }
    totalDancesGraph();

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
                    <h3>Please wait.. </h3> <br />
                    <p>If you have not dance yet, please head over to practice mode for us to analyse your dances!</p>
                </Container>
                :
                <Container fluid>
                    <h2>Welcome, {username}</h2>
                    <Row>
                        <Col lg={3} sm={6}>
                            <StatsCard
                                bigIcon={<i className="pe-7s-date text-success" />}
                                statsText="Consecutive days danced"
                                statsValue="1"
                            />
                        </Col>
                        <Col lg={3} sm={6}>
                            <StatsCard
                                bigIcon={<i className="pe-7s-graph1 text-danger" />}
                                statsText="Total dances"
                                statsValue={totalDances}
                            />
                        </Col>
                    </Row>
                    <Row>
                        <Col md={6}>
                            <Card
                                id="chartTimeseries"
                                title="Cumulative total dances"
                                content={
                                    <div className="ct-chart">
                                        <ChartistGraph
                                            data={totalDancesGraph()}
                                            type="Line"
                                            options={options}
                                            responsiveOptions={responsiveSales}
                                        />
                                    </div>
                                }
                                legend={
                                    <div className="legend">{createLegend(legendSales)}</div>
                                }
                            />
                        </Col>
                        <Col md={3}>
                            <Card
                                title="Dance accuracy"
                                content={
                                    <div
                                        id="chartPreferences"
                                        className="ct-chart ct-perfect-fourth"
                                    >
                                        <ChartistGraph data={danceAccuracy()} type="Pie" />
                                    </div>
                                }
                                legend={
                                    <div className="legend">{createLegend(legendPie)}</div>
                                }
                            />
                        </Col>
                    </Row>
                </Container>
            }
        </div>
    )
}