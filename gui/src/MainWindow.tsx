import { getFigureData, getFileData, readDir, startListeningToParent } from "@figurl/interface";
import { FunctionComponent, useEffect, useState } from "react";
import { SetupTimeseriesSelection } from "./package/context-timeseries-selection";
import { useRoute } from "./route";
import useWindowDimensions from "./useWindowDimensions";
import View from "./View";

const urlSearchParams = new URLSearchParams(window.location.search)
const queryParams = Object.fromEntries(urlSearchParams.entries())

const opts = {}

const MainWindow: FunctionComponent = () => {
    const { width, height } = useWindowDimensions()
    const [figureData, setFigureData] = useState<any>(undefined)
    const {urlState} = useRoute()
    useEffect(() => {
        (async () => {
            const data = await getFigureData()
            if (data && (data.type)) {
                setFigureData(data)
            }
            else if (urlState.figure) {
                // read rtcshare dir
                const dd = await getFileData(`$dir/figures/${urlState.figure}/_main.json`, () => {}, {responseType: 'json-deserialized'})
                for (const view of dd.views) {
                    if (view.dataUri.startsWith('./')) {
                        view.dataUri = `$dir/figures/${urlState.figure}/${view.dataUri.slice(2)}`
                    }
                }
                setFigureData(dd)
            }
        })()
    }, [urlState.figure])
    if (!figureData) return <div>Loading...</div>
    return (
        <SetupTimeseriesSelection>
            <View
                data={figureData}
                width={width}
                height={height}
                opts={opts}
            />
        </SetupTimeseriesSelection>
    )
}

if (queryParams.figureId) {
    startListeningToParent()
}

export default MainWindow