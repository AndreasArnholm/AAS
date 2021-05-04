// App.js
import { useReducer, useEffect, useState, forwardRef } from 'react'
import { Grid, withStyles, Button } from '@material-ui/core'
import RobotComponents from './robotComponents'
import ModalAppBar from './entitybar'
import Dialog from '@material-ui/core/Dialog'
import DialogActions from '@material-ui/core/DialogActions'
import DialogContent from '@material-ui/core/DialogContent'
import DialogContentText from '@material-ui/core/DialogContentText'
import DialogTitle from '@material-ui/core/DialogTitle'
import Slide from '@material-ui/core/Slide'
import axios from 'axios'
import configs from '../config.json'

// Import worker for testing
import worker from 'workerize-loader!./../testWorker' // eslint-disable-line import/no-webpack-loader-syntax

const Transition =  forwardRef(function Transition(props, ref) {
  return <Slide direction="up" ref={ref} {...props} />
})

const styles = theme => ({
  paper: {
    backgroundColor: '#fbfbfb', //theme.palette.background.paper,
    boxShadow: theme.shadows[5],
  }
})

function reducer(state, action){
  switch (action.type){
    case 'update':
      return {
        ...state,
        components: action.components
      }
    case 'camera_start':
      return {
        ...state,
        streamURL: action.streamURL,
        cameraButton: "Stop",
        cameraIconButton: true
      }
    case 'camera_stop':
      return {
        ...state,
        cameraButton: "Start",
        cameraIconButton: false
      }
      case 'camera_icon_event':
        return {
          ...state,
          cameraIconButton: !state.cameraIconButton
        }
      default: 
        return state
    }
  }
  
  function Robot(props) {
    const [alertOpen, setAlertOpen] = useState(false)
    const [robotState, dispatch] = useReducer(reducer, {
      components: {},
      cameraButton: localStorage.getItem('camera_opened_' + props.robot.rid) || "Start",
      cameraIconButton: localStorage.getItem('camera_window_opened_' + props.robot.rid) === "true",
      streamURL: null
    })

    const fetch = (rid) => {
      axios.get(configs.API_URL + "api/robots/" + rid).then(resp => {
        dispatch({type: 'update',
                  components: resp.data.components})
      })
    }

    const onStatusUpdate = (data) => {
      const object = JSON.parse(data)
      if(object.rid === props.robot.rid){
        fetch(object.rid)
      }
    }
    
    const handleCameraEvent = () => {
      if(robotState.cameraButton.localeCompare("Stop") == 0){
        handleAlertOpen()
      } else {
        handleCameraOpen()
      }
    }

    const sendCameraEvent = () => {
      props.ws.emit("camera_event", {'camera_event': robotState.cameraButton, 'rid': props.robot.rid})
    }

    const setCameraStopped = () => {
      dispatch({
        type: 'camera_stop',
      })
      localStorage.setItem('camera_opened_' + props.robot.rid, "Start")
      localStorage.setItem('camera_window_opened_' + props.robot.rid, false)
    }

    const handleCameraClose = () => {
      sendCameraEvent()
      setCameraStopped()
      handleAlertClose()
    }

    const handleCameraOpen = () => {
      sendCameraEvent()
      axios.get(configs.API_URL + "api/robots/" + props.robot.rid + "/video").then(resp => {
        dispatch({
          type: 'camera_start',
          streamURL: resp.data.url + "/video",
        })
        localStorage.setItem('camera_stream_url_' + props.robot.rid, resp.data.url + "/video")
      })
      localStorage.setItem('camera_opened_' + props.robot.rid, "Stop")
      localStorage.setItem('camera_window_opened_' + props.robot.rid, true)
    }

    const handleCameraIconEvent = () => {
      localStorage.setItem('camera_window_opened_' + props.robot.rid, !robotState.cameraIconButton)
      dispatch({
        type: 'camera_icon_event',
      })
    }
    
    const handleAlertOpen = () => {
      setAlertOpen(true)
    }

    const handleAlertClose = () => {
      setAlertOpen(false)
    }

    const handleTest = () => {
      const testWorker = worker()
      // testWorker.addEventListener('message', (message) => {
      //   console.log(message.data)
      // })
      // testWorker.runTests(2)
      testWorker.postMessage({val: 5})
      testWorker.onerror = (err) => err
      testWorker.onmessage = (e) => {
        console.log(e.data)
      }
    }

    useEffect(() => {
      dispatch({type: 'update', 
                components: props.robot.components})
      try{
        props.ws.on('status', onStatusUpdate)
      } catch (e){
        console.log("Websocket is not connected!")
      }

      // Destroy listener
      return () => {
        props.ws.off('status', onStatusUpdate)
      }
    }, [])


    const { classes } = props
    return (
      <div className={classes.paper}>
        <ModalAppBar 
          ws={props.ws} 
          rid={props.robot.rid}
          stopCamera={setCameraStopped}
          close={props.close}/>
        <RobotComponents 
          rid={props.robot.rid}
          name={props.robot.name}
          ws={props.ws}
          state={robotState}
          handleCameraEvent={handleCameraEvent}
          handleCameraIconEvent={handleCameraIconEvent}
          handleTest={handleTest}
        />
        <Dialog
          open={alertOpen}
          TransitionComponent={Transition}
          keepMounted
          onClose={handleAlertClose}
        >
          <DialogTitle>{"You are about to stop the video stream for the robot entity completely!"}</DialogTitle>
          <DialogContent>
            <DialogContentText>
              This will stop the video stream for every operator currently monitoring this specific robot. To close the video stream window without stopping the stream, simply use the camera icon button.
            </DialogContentText>
          </DialogContent>
          <DialogActions>
            <Button onClick={handleAlertClose} color="primary">
              Cancel
            </Button>
            <Button onClick={handleCameraClose} color="primary" disabled={!(localStorage.getItem('admin') === 'true')}>
              (Admin) Stop video stream
            </Button>
          </DialogActions>
        </Dialog>
      </div>
    )
  }

export default withStyles(styles)(Robot)