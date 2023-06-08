import { FunctionComponent, useCallback, useMemo } from "react";
import { useTimeRange, useTimeseriesSelection } from "../../context-timeseries-selection";
// import PoseViewport from "./PoseViewport";
import useWheelZoom from "./useWheelZoom";
import VideoFrameView from "./VideoFrameView";

type Props ={
	width: number
	height: number
	videoUri: string
	videoWidth: number
	videoHeight: number
	samplingFrequency: number
	// canEditPose: boolean
	onSelectRect?: (r: {x: number, y: number, w: number, h: number}) => void
}

const CameraViewArea: FunctionComponent<Props> = ({width, height, videoUri, videoWidth, videoHeight, samplingFrequency, onSelectRect}) => {
	const {currentTime, setCurrentTime} = useTimeseriesSelection()
	const {visibleStartTimeSec, visibleEndTimeSec, setVisibleTimeRange} = useTimeRange()
	const W = videoWidth * height < videoHeight * width ? videoWidth * height / videoHeight : width
	const H = videoWidth * height < videoHeight * width ? height : videoHeight * width / videoWidth
	const rect = useMemo(() => ({
		x: (width - W)  / 2,
		y: (height - H) / 2,
		w: W,
		h: H
	}), [W, H, width, height])
	const {affineTransform, handleWheel} = useWheelZoom(rect.x, rect.y, rect.w, rect.h)
	const handleSetTimeSec = useCallback((t: number) => {
		setCurrentTime(t)
		if ((visibleStartTimeSec !== undefined) && (visibleEndTimeSec !== undefined)) {
			if ((t < visibleStartTimeSec) || (t > visibleEndTimeSec)) {
				let delta = t - (visibleStartTimeSec + visibleEndTimeSec) / 2
				if (visibleStartTimeSec + delta < 0) delta = -visibleStartTimeSec
				setVisibleTimeRange(visibleStartTimeSec + delta, visibleEndTimeSec + delta)
			}
		}
	}, [visibleStartTimeSec, visibleEndTimeSec, setVisibleTimeRange, setCurrentTime])
	return (
		<div style={{position: 'absolute', width, height}} onWheel={handleWheel}>
			<div className="video-frame" style={{position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h}}>
				<VideoFrameView
					width={rect.w}
					height={rect.h}
					timeSec={currentTime}
					setTimeSec={handleSetTimeSec}
					src={videoUri}
					affineTransform={affineTransform}
				/>
			</div>
			{/* <div className="pose-viewport" style={{position: 'absolute', left: rect.x, top: rect.y, width: rect.w, height: rect.h}}>
				<PoseViewport
					width={rect.w}
					height={rect.h}
					videoWidth={video.width}
					videoHeight={video.height}
					canEditPose={canEditPose}
					videoSamplingFrequency={video.samplingFrequency}
					affineTransform={affineTransform}
					onSelectRect={onSelectRect}
				/>
			</div> */}
		</div>
	)
}

export default CameraViewArea
