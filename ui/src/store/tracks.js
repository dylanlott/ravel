import API from '@/api'

const tracks = {
    namespaced: true,
    state: {
      list: [],
      current: {
        id: '',
        name: '',
        info: '',
        user_id: '',
        trackouts: [],
      },
      error: "",
      loading: false
    },
    mutations: {
      'TRACK_REQUEST' (state) {
        state.loading = true
      },
      'TRACK_SUCCESS' (state, tracks) {
        state.loading = false
        state.list = tracks
      },
      'GET_ONE_TRACK_SUCCESS' (state, track) {
        state.loading = false
        state.current = {
          id: track.payload.id,
          name: track.payload.name,
          info: track.payload.info,
          user_id: track.payload.user_id,
          trackouts: []
        }
      },
      'GET_TRACKOUTS' (state) {
        state.loading = true
      },
      'GET_TRACKOUTS_SUCCESS' (state, trackouts) {
        console.log('trackouts: ', trackouts)
        state.loading = false
        state.current.trackouts = trackouts
      },
      'GET_TRACKOUTS_FAILURE' (state, err) {
        state.loading = false
        state.error = err
      },
      'TRACK_FAILURE' (state) {
        state.loading = false
      },
      'TRACKOUT_REQUEST' (state) {
        state.loading = true
      },
      'TRACKOUT_SUCCESS' (state, trackout) {
        state.loading = false
        state.current = trackout
        state.error = undefined
      },
      'ADD_TRACKOUT_SUCCESS' (state, trackouts) {
        state.loading = false
        state.error = undefined
        state.current.trackouts.push(trackout)
      },
      'TRACKOUT_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'DELETE_TRACK_SUCCESS' (state, track_id) {
        // TODO: Remove track from list with splice
        state.loading = false
        state.error = undefined
      }, 
      'DELETE_TRACK_FAILURE' (state, error) {
        state.error = error
        state.loading = false
      },
      'UPDATE_TRACKOUT_WAV_SUCCESS' (state, data) {
        state.error = ""
        state.loading = false
        console.log('update trackout wav success: ', data)
      }
    },
    actions: {
      async create ({ commit, state }, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().post('/tracks', {
          	"name": track.name,
          	"user_id": track.user_id,
          	"artist": track.artist,
          	"info": track.info
          })
          commit('TRACK_SUCCESS', data)
        } catch (err) {
          commit('TRACK_FAILURE', err)
        }
      },
      async get ({ commit, state }) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get('/tracks')
          console.table(data.payload)
          commit('TRACK_SUCCESS', data.payload)
        } catch (err) {
          console.log('error getting tracks: ', err)
          return err
        }
      },
      async getTrackDetails ({ commit, dispatch }, id) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`)
          commit('GET_ONE_TRACK_SUCCESS', data)
        } catch (err) {
          console.error(err)
          return err
        }
      },
      async getTrackouts({ commit }, trackID) {
        try {
          commit('GET_TRACKOUTS')
          let { data } = await API().get(`/trackouts`, {
            track_id: trackID
          })
          commit('GET_TRACKOUTS_SUCCESS', data.payload)
        } catch (err) {
          commit('GET_TRACKOUTS_FAILURE', err)
          console.error(err)
          return err
        }
      },
      async addTrackout({ commit }, trackout) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().post('/trackouts', trackout)
          commit('ADD_TRACKOUT_SUCCESS', data.payload)
        } catch (err) {
          throw new Error('error processing trackout: ', err)
        }
      },
      async update({ commit }, track) {
        try {
          commit('TRACK_REQUEST')
          let { data } = await API().get(`/tracks/${id}`, track)
          commit('TRACK_SUCCESS')
        } catch (err) {
          commit('TRACK_FAILURE')
          console.log('error updating track: ', err)
        }
      },
      async delete ({ commit }, track) {
        try {
          let { data } = await api.delete(`/tracks/${track.id}`)
          commit('DELETE_TRACK_SUCCESS')
        } catch (err) {
          commit('DELETE_TRACK_FAILURE', err)
          console.error('failed to delete track')
        }
      },
      async uploadFile ({ commit, state }, payload) {
        try {
          let { data } = await api.post(`/trackouts/wav/${payload.id}`)
          commit('UPLOAD_SUCCESS', data)
        } catch (err) {
          if (err.response) {
            console.log('error response: ', err.response)
          }
          console.error('error uploading file: ', err)
          throw new Error(err)
        }
      },
      async createTrackoutWithoutWav ({ commit, state }, trackout) {
        try {
          const id = window.localStorage.getItem('user_id')
          let { data } = await API().post('/trackouts', {
            // TODO: set these correctly
            owner_id : id,
            user_id : id,
            name : trackout.name,
            type : trackout.type,
            settings : {
              eq: {},
              compression: {}
            },
            wavefile : trackout.wavefile,
            track_id : trackout.track_id
          })
          commit('ADD_TRACKOUT_SUCCESS', data)
        } catch (err) {
          console.error(err)
          throw new Error(err)
        }
      },
      async updateTrackoutWithWav ({ commit, state }, formData) {
        try {
          let { data } = await API().put()
          commit('UPDATE_TRACKOUT_WAV_SUCCESS', data)
        } catch (err) {
          console.error('update trackout wav success error: ', err)
        }
      }
    }
}

export default tracks
