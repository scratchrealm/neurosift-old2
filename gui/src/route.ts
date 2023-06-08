import {useUrlState} from '@figurl/interface'

export const useRoute = () => {
    const {urlState} = useUrlState()

    return {urlState}
}