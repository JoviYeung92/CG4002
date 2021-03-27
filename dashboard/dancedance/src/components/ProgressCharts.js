import React from 'react';
import ChartistGraph from "react-chartist";
import {
    dataBar,
    dataSales,
    optionsSales,
    responsiveSales,
  } from "../component_variables/Variables";
import { ACCURACYGRAPH } from './Constants';

export const ProgressCharts = ({graphType, data}) => {

    var options = {
        low: 0,
        high: 1,
        showArea: false,
        axisX: {
            showGrid: false,
        },
        scaleMinSpace: 600,
        lineSmooth: true,
        showLine: true,
        showPoint: true,
        fullWidth: true,
        chartPadding: {
            right: 50
        }
    };
    return (
        graphType === ACCURACYGRAPH ? 
        <ChartistGraph
            data={data}
            type="Line"
            // options={options}
            // responsiveOptions={responsiveSales}
        /> :
        <ChartistGraph
           data={data} 
           type="Bar"
        />
    )
}