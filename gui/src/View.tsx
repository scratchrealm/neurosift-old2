import { default as loadNeurosiftView } from './package/loadView';
import { FunctionComponent, useMemo } from 'react';

type Props = {
    data: any
    width: number
    height: number
}

const View: FunctionComponent<Props> = ({data, width, height}) => {
    // It's important to memoize this
    // because validation of data can be slow
    const v = useMemo(() => {
        const viewLoaders = [loadNeurosiftView]
        for (const loadView of viewLoaders) {
            const v = loadView({data, width, height})
            if (v) return v
        }
    }, [data, height, width])
    if (v) return v

    console.warn(data)
    return (
        <div>Invalid view data: {data.type}</div>
    )
}

export default View