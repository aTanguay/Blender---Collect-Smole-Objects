# Blender - Collect Smole Objects Addon
 A simple blender addon that will collect up any object smaller, by volume, than the currently selected object.

This addon is maninly useful for people who have to deal with CAD data collections like automotive UDMs.
Often times these collections come in with a lot of parts you don't need because they fell through the cracks or something when someone was exporting...things like screws and springs and whatnot that you won't see when rendering. Sometimes these can be very dense, adding bulk that you don't want - and/or can't afford - in your scene. You don't want a small bolt taking up more polys than your whole hood.

To use the addon, install as usual. Once installed, you will find it in the 'Select' menu in the main 3D interface.
At the end of the menu, after a separator you should see 'Collect Smaller Objects' (see below).

Select ONE mesh object in your scene. Everything smaller than this object will be automatically placed into a collection called 'Littles'. So, select your object - start out very small - run 'Collect Smaller Objects'. The tiny stuff should disappear. The collection will also be automatically hidden. Objects are still there, but they're hidden in this collection.

That's it. You can run the script again, and it will automatically place new objects in that collection. So, you can start small and work your way up and see what effect it's having on your scene.
From there, you could export these objects and purge your scene, or just keep them hidden. That's your business.

![Menu](dev/ss_01.png)


(Once again, a sweet ChatGPT joint, featuring me. Yes, it may destroy us all, but for now, neat.)
