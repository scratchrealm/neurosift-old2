import React from "react"
import { ViewComponentProps } from "@figurl/core-views"
import { FunctionComponent } from "react"
import { isTimeseriesGraphViewData, TimeseriesGraphView } from "./view-timeseries-graph"
import { isRasterPlotView2Data, RasterPlotView2 } from "./view-raster-plot-2"

const loadView = (o: {data: any, width: number, height: number, opts: any, ViewComponent: FunctionComponent<ViewComponentProps>}) => {
    const {data, width, height} = o
    if (isTimeseriesGraphViewData(data)) {
        return <TimeseriesGraphView data={data} width={width} height={height} />
    }
    else if (isRasterPlotView2Data(data)) {
        return <RasterPlotView2 data={data} width={width} height={height} />
    }
    else return undefined
}

export default loadView