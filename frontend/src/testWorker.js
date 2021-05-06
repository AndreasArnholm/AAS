import socket from './websocket'

// onmessage = (e) => {
//     var ret = []
//     for(let i = 0; i < e.data.val; i++){
//         const startTime = new Date().getTime()
//         setTimeout(function() {
//             ret.push(new Date().getTime() - startTime)
//             socket.emit('worker', { "command" : "worker_command" })
//             postMessage(ret)
//         }, 1000*i)
//     }
// }

//const CMD_CYCLE = ["camera_event:start", "command:kmp", "command:lbr", "camera_event"]

//props.ws.emit("camera_event", {'camera_event': robotState.cameraButton, 'rid': props.robot.rid})

//props.ws.emit('command', { "command" : "kmp:" + speed + vector, 'rid': props.rid})
//vector = " 1 0 0"
//speed = "0.1"

//props.ws.emit('command', { "command" : "lbr:" + joint + " " + direction, 'rid': props.rid})
// "A4","1"

onmessage = (e) => {
    (function myLoop(i, camera_on, kmp) {
        setTimeout(function() {
            if(i % 50 === 0){
                if(camera_on){
                    camera_on = false
                    socket.emit('worker', { "command" : "camera_off" })
                    //socket.emit("camera_event", {'camera_event': 'stop', 'rid': 1})
                } else {
                    camera_on = true
                    socket.emit('worker', { "command" : "camera_on" })
                    //socket.emit("camera_event", {'camera_event': 'start', 'rid': 1})
                }
            }
            if(kmp){
                kmp = false
                socket.emit('worker', { "command" : "kmp_command" })
                //socket.emit('command', { "command" : "kmp:" + '0.1 0 0 1', 'rid': 1})             
            } else {
                kmp = true
                socket.emit('worker', { "command" : "lbr_command" })
                //socket.emit('command', { "command" : "lbr:" + "A7" + " " + "1", 'rid': props.rid})        
            }
            if(--i){
                //postMessage(i)
                myLoop(i, camera_on, kmp)   //  decrement i and call myLoop again if i > 0
            } else {
                postMessage("Test completed")
            }
        }, 1000)
    })(e.data.val, false, false)
}