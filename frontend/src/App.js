// App.js
import { useEffect, useCallback, useState } from 'react'
import DenseAppBar from './components/appbar'
import Entity from './components/entity'
import KMR from './components/kmr'
import { Grid, Button, withStyles, Backdrop, Modal, Fade } from '@material-ui/core'
import history from './history'
import Sarus from '@anephenix/sarus';
import configs from './config.json'

const styles = theme => ({
  root: {
    flexGrow: 1,
    padding: theme.spacing(10,0,0),
  },
  card: {
    margin: theme.spacing.unit*3,
  },
  margin: {
      margin: theme.spacing(2),
  },
  padding: {
      padding: theme.spacing(1)
  },
  modal: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  popup: {
    [theme.breakpoints.down('xs')]: {
      height: '100%',
      overflow: "auto"
    },
  }
});

function App(props) {
  const [kmpStatus, setKmpStatus] = useState(false);
  const [lbrStatus, setLbrStatus] = useState(false);
  const [componentsOpen, setComponentsOpen] = useState(false)
  const [image, setImage] = useState("")

  const handleComponentsOpen = () => {
    setComponentsOpen(true);
  };

  const handleComponentsClose = () => {
    setComponentsOpen(false);
  };

  useEffect(() => {
    new Sarus({
      url: configs.WS_URL + "ws/",
      eventListeners: {
          open: [connectionOpened],
          message: [updateTimeline],
          close: [connectionClosed],
          error: [throwError]
      } 
    });

    new Sarus({
      url: configs.WS_URL + "stream/",
      eventListeners: {
          open: [streamConnectionOpened],
          message: [updateFrame],
          close: [streamConnectionClosed],
          error: [throwError]
      } 
    });
  }, [])
  
  const connectionOpened = () => console.log("Socket connection opened");

  const connectionClosed = () => console.log("Socket connection closed");

  const streamConnectionOpened = () => console.log("Stream socket connection opened");

  const streamConnectionClosed = () => console.log("Stream socket connection closed");

  const throwError = error => {
      throw error;
  }

  const updateTimeline = useCallback((event) => {
      const object = JSON.parse(event.data)
      console.log(object)

      if(object.robot == "KMR"){
          if(object.component == "kmp"){
            setKmpStatus(object.component_status); 
          }
          if(object.component == "lbr"){
            setLbrStatus(object.component_status); 
          }
        }
  }, [])

  const updateFrame= useCallback((frame) => {
    setImage(frame.data)
}, [])

  const { classes } = props
  return (
      <div style={{background: '#fbfbfb'}}>
        <DenseAppBar />
        {/*<Grid container direction="column" justify="center" alignItems="center" style={{ minHeight: '100vh' }}>
          <Button onClick={handleComponentsOpen} >
            <Entity kmpStatus={kmpStatus} lbrStatus={lbrStatus}/>
          </Button>
        </Grid>*/}
        <Grid container justify="center" className={classes.root}>
          {[1,2,3,4,5,6].map((value) => (
            <Grid item className={classes.card} xs={5} sm={4} md={3} lg={2}>
              <Button onClick={handleComponentsOpen}>
                <Entity 
                  kmpStatus={kmpStatus} 
                  lbrStatus={lbrStatus}
                  num={value}/>
              </Button>
            </Grid>
          ))}
        </Grid>
          <Grid><img src={`data:image/png;base64,${image}`}/></Grid>
        <Modal
          aria-labelledby="transition-modal-title"
          aria-describedby="transition-modal-description"
          className={classes.modal}
          open={componentsOpen}
          onClose={handleComponentsClose}
          closeAfterTransition
          BackdropComponent={Backdrop}
          BackdropProps={{
            timeout: 500,
          }}
        >
          <Fade in={componentsOpen}>
            <div className={classes.popup}>
              <KMR kmp={kmpStatus} lbr={lbrStatus} close={handleComponentsClose}/>  
            </div>
          </Fade>
        </Modal>
      </div>
    )
}

export default withStyles(styles)(App)