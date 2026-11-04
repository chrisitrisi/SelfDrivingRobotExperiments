// Tumbler R2, mm. PCB top z=0; sensors point towards negative z.
// Universal adapter. Chassis interface requires fit check.
// part: holder, shim05, shim1, assembly.
part="holder"; standoff=6; frame_t=3; $fn=64;
module slot(x,y1,y2,d,h,z){translate([x,0,z])hull(){translate([0,y1,0])cylinder(d=d,h=h);translate([0,y2,0])cylinder(d=d,h=h);}}
module holder(){difference(){
 union(){
  for(x=[4,72]){
   translate([x-4,4,standoff])cube([8,66,frame_t]);
   translate([x,4,standoff])cylinder(d=8,h=frame_t);
   for(y=[4,28])translate([x,y,0])cylinder(d=6.4,h=standoff+frame_t);
  }
  translate([4,36,standoff])cube([68,8,frame_t]);
 }
 for(x=[4,72])for(y=[4,28]){
  translate([x,y,-.1])cylinder(d=3.4,h=standoff+frame_t+.2);
  translate([x,y,standoff+frame_t-2.5])rotate([0,0,30])cylinder(d=5.7/cos(30),h=2.6,$fn=6);
 }
 for(x=[4,72])slot(x,46,66,3.4,frame_t+.2,standoff-.1);
 for(x=[33,43])translate([x-1,38,standoff-.1])cube([2,4,frame_t+.2]);
}}
module shim(t){difference(){cylinder(d=6,h=t);translate([0,0,-.1])cylinder(d=3.4,h=t+.2);}}
module assembly(){
 color("orange")holder();
 color([.05,.35,.18])translate([0,0,-1.6])difference(){cube([76,32,1.6]);for(x=[4,72])for(y=[4,28])translate([x,y,-.1])cylinder(d=3.2,h=1.8);}
 for(x=[13:10:63])color([.15,.15,.15])translate([x-3.5,5.5,-8.1])cube([7,7,6]);
 color("white")translate([30.1,26.4,0])cube([15.8,4.1,4.2]); // approximate connector envelope
}
if(part=="holder")holder();
if(part=="shim05")shim(.5);
if(part=="shim1")shim(1);
if(part=="assembly")assembly();
