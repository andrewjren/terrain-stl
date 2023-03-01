// includes 
include <terrain_vector.scad>


// TerrainBlock module should define an individual block in the
// terrain map.
module TerrainBlock(start_point=[0,0,0],
                    width=1,
                    altitudes=[1,1,1,1]) 
{
    x = start_point[0];
    y = start_point[1];
    z = start_point[2]-0.001;

    TerrainBlockPoints = [
      [  x,  y,  z ],  //0
      [ x+width,  y,  z ],  //1
      [ x+width,  y+width,  z ],  //2
      [  x,  y+width,  z ],  //3
      [  x,  y,  altitudes[0]],  //4
      [ x+width, y,  altitudes[1] ],  //5
      [ x+width,  y+width,  altitudes[2] ],  //6
      [  x,  y+width,  altitudes[3] ]]; //7
      
    TerrainBlockFaces = [
      [0,1,2,3],  // bottom
      [4,5,1,0],  // front
      [6,5,4],  // top triangle
      [7,6,4],  // top other triangle
      [5,6,2,1],  // right
      [6,7,3,2],  // back
      [7,4,0,3]]; // left
      
    polyhedron( TerrainBlockPoints, TerrainBlockFaces );
}

module TerrainMap()
{
    // iterate through each element in terrain_vector and generate
    // TerrainBlocks for each of them 
    for(x_idx = [num_samples-2:-1:0]) 
    {
        for(y_idx = [num_samples-2:-1:0])
        {
            dx = x_idx*sample_size+0.001;
            dy = y_idx*sample_size+0.001;
            
            TerrainBlock(start_point=[dx,dy,0],
                         width=sample_size,
                         altitudes=[terrain_vector[x_idx][y_idx]/scale,
                                    terrain_vector[x_idx+1][y_idx]/scale,
                                    terrain_vector[x_idx+1][y_idx+1]/scale,
                                    terrain_vector[x_idx][y_idx+1]/scale]
            );
        }
    }
}

module TerrainLabel(label, xoffset, yoffset, height_of_base)
{
    translate([xoffset, yoffset, height_of_base])
    {
        linear_extrude(height = 2, center = false) {
            text(label,size = 4, font = "tohoma");
        }
    }
}

height_of_base = 2;
length_of_base = sample_size*num_samples;

TerrainLabel("Oahu",2,2,1);
cube([length_of_base, length_of_base, height_of_base+0.001]);


translate([0,0,height_of_base]){
    TerrainMap();
}

