import { useState, useEffect} from 'react';
import { Paper, withStyles, Grid, Button, Slider } from '@material-ui/core';
import { ArrowUpwardRounded, ArrowDownwardRounded, ArrowBack, ArrowForward, RotateLeft, RotateRight, ThumbUpSharp} from '@material-ui/icons'
import axios from 'axios';
import configs from '../../config.json'

const styles = theme => ({
    margin: {
        margin: theme.spacing(2),
    },
    padding: {
        padding: theme.spacing(1)
    }
});

function KMPController(props) {
    const [speed, setSpeed] = useState(0.1)
    const [enabled, setEnabled] = useState(false)

    useEffect(() => {
        axios.get(configs.API_URL + "robots/1").then(resp => {
            setEnabled(resp.data.kmp)
        });
    })

    const handleOnChangeSpeed = (event, newValue) => {
        setSpeed(newValue)
    };

    const moveKMP = (direction) => {
        var vector = null

        if(direction === "up"){
            vector = " 1 0 0"
        }
        if(direction === "down"){
            vector = " -1 0 0"
        }
        if(direction === "left"){
            vector = " 0 1 0"
        }
        if(direction === "right"){
            vector = " 0 -1 0"
        }
        if(direction === "clockwise"){
            vector = " 0 0 -1"
        }
        if(direction === "counter-clockwise"){
            vector = " 0 0 1"
        }
        if(direction === "stop"){
            vector = " 0 0 0"
        }
        
        axios.post(configs.API_URL + "commands/", { "command" : "kmp:" + speed + vector})
    }

    const defaultColor = "white"
    const pressColor = "gray"

    const [upColor, setUpColor] = useState(defaultColor)
    const [downColor, setDownColor] = useState(defaultColor)
    const [leftColor, setLeftColor] = useState(defaultColor)
    const [rightColor, setRightColor] = useState(defaultColor)
    const [counterClockwiseColor, setCounterClockwiseColor] = useState(defaultColor)
    const [clockwiseColor, setClockwiseColor] = useState(defaultColor)

    document.onkeydown = function(event) {
        if (event.key == 'ArrowUp' && upColor==defaultColor) {
            moveKMP("up")
            console.log("ArrowUp pressed")
            setUpColor(pressColor)
        };
        if (event.key == 'ArrowDown' && downColor==defaultColor) {
            moveKMP("down")
            console.log("ArrowDown pressed")
            setDownColor(pressColor)
        };
        if (event.key == 'ArrowLeft' && leftColor==defaultColor) {
            moveKMP("left")
            console.log("ArrowLeft pressed")
            setLeftColor(pressColor)
        };
        if (event.key == 'ArrowRight' && rightColor==defaultColor) {
            moveKMP("right")
            console.log("ArrowRight pressed")
            setRightColor(pressColor)
        };
        if (event.key == 'o' && counterClockwiseColor==defaultColor) {
            moveKMP("counter-clockwise")
            console.log("CounterClockwise pressed")
            setCounterClockwiseColor(pressColor)
        };
        if (event.key == 'p' && clockwiseColor==defaultColor) {
            moveKMP("clockwise")
            console.log("clockwise pressed")
            setClockwiseColor(pressColor)
        };
    };

    document.onkeyup = function(event) {
        if (event.key == 'ArrowUp') {
            moveKMP("stop")
            console.log("ArrowUp released")
            setUpColor(defaultColor)
        };
        if (event.key == 'ArrowDown') {
            moveKMP("stop")
            console.log("ArrowDown released")
            setDownColor(defaultColor)
        };
        if (event.key == 'ArrowLeft') {
            moveKMP("stop")
            console.log("ArrowLeft released")
            setLeftColor(defaultColor)
        };
        if (event.key == 'ArrowRight') {
            moveKMP("stop")
            console.log("ArrowRight released")
            setRightColor(defaultColor)
        };
        if (event.key == 'o') {
            moveKMP("stop")
            console.log("CounterClockwise released")
            setCounterClockwiseColor(defaultColor)
        };
        if (event.key == 'p') {
            moveKMP("stop")
            console.log("clockwise released")
            setClockwiseColor(defaultColor)
        };
    };

    const { classes } = props;
    return (
        <Paper className={classes.padding}>
            <Grid container justify="center">
                <div> KMP Controller </div>
            </Grid>
            <div className={classes.margin} >
                Speed <Slider
                defaultValue={0.1}
                step={0.1}
                min={0.0}
                max={1.0}
                marks
                valueLabelDisplay="auto"
                onChange={handleOnChangeSpeed}
                disabled={!enabled} 
                />
                <Grid container justify="center" style={{ marginTop: '10px' }}>
                    <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('up')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: upColor}}><ArrowUpwardRounded /></Button>
                </Grid>
                <Grid container justify="center" style={{ marginTop: '10px' }}>
                    <Grid>
                        <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('left')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: leftColor}}><ArrowBack /></Button>
                    </Grid>
                    <Grid>
                        <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('down')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: downColor}}><ArrowDownwardRounded /></Button>
                    </Grid>
                    <Grid>
                        <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('right')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: rightColor}}><ArrowForward/></Button>
                    </Grid>
                </Grid>
                <Grid container justify="center" style={{ marginTop: '10px' }}>
                    <Grid>
                        <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('counter-clockwise')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: counterClockwiseColor}}><RotateLeft /></Button>
                    </Grid>
                    <Grid>
                        <Button disabled={!enabled} onMouseUp ={() => moveKMP('stop')} onMouseDown ={() => moveKMP('clockwise')} variant="outlined" color="primary" style={{ textTransform: "none", backgroundColor: clockwiseColor}}><RotateRight /></Button>
                    </Grid>
                </Grid>
            </div>
        </Paper>
    );
    
}

export default withStyles(styles)(KMPController)