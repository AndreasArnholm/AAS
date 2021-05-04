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
    (function myLoop(i) {
        setTimeout(function() {
            socket.emit('worker', { "command" : "worker_command" })                
            if (--i){
                myLoop(i)   //  decrement i and call myLoop again if i > 0
            } else {
                postMessage("Test completed")
            }
        }, 1000)
    })(e.data.val)
}