import { useState } from 'react';
import { Grid, withStyles, Button, Grow } from '@material-ui/core'
import CircularProgress from '@material-ui/core/CircularProgress'
import KMRGeneralCommands from './kmr_components/kmrGeneralCommands'
import KMPController from './kmr_components/kmpController'
import LBRController from './kmr_components/lbrController'
import VideoComponent from './video'

const styles = theme => ({
    root: {
      flexGrow: 1,
      padding: theme.spacing(2,4,3),
      borderRadius: 2,
    }
  })

function RobotComponents(props) {
    
    const { classes } = props
    return (
        <Grid container className={classes.root} spacing={3}>
            <Grid item xs={12}>
                {
                    // KMR iiwa components
                    props.name === 'KMR' && 
                    <Grid container justify="center" spacing={3}>
                        <Grid item>
                            <KMPController ws={props.ws} status={props.state.components.kmp} rid={props.rid}/>
                        </Grid>
                        <Grid item>
                            <LBRController ws={props.ws} status={props.state.components.lbr} rid={props.rid}/>
                        </Grid>
                        <Grid item>
                            <VideoComponent 
                                rid={props.rid}
                                state={props.state}
                                handleCameraEvent={props.handleCameraEvent}
                                handleCameraIconEvent={props.handleCameraIconEvent}
                            />
                        </Grid>
                        <Grid item>
                            <KMRGeneralCommands ws={props.ws}/>
                        </Grid>
                        <Grid item>
                            <Button onClick={props.handleTest}>
                                test
                            </Button>
                        </Grid>
                    </Grid>
                }

                {
                    // (INSERT ROBOT HERE) components
                }
            </Grid>
        </Grid>
    )
}

export default withStyles(styles)(RobotComponents)