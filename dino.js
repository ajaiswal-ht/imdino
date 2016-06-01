var http = new XMLHttpRequest();setInterval(function(){
var obs = Runner.instance_.horizon.obstacles.length;
if(obs==0){
  var fs = null;
  var fd = null;
}
else{
   var fs=Runner.instance_.horizon.obstacles[0].width;
   var fd=Runner.instance_.horizon.obstacles[0].xPos;}
var d = { "s": Runner.instance_.currentSpeed/13, "fs":fs/60.0 , "fd": fd/50.0, "sc": Runner.instance_.distanceRan*.025, "o":Runner.instance_.crashed , "n": obs}
var url='http://127.0.1:5000/?r='+JSON.stringify(d);http.open("GET", url);
http.send(null);console.log('yes');}, 90)