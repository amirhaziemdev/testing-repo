A README FILES TO OUTLINE THE CHANGES AND NOTES ON WHAT HAS BEEN DONE TO THE INSPECTION SYSTEM
----------------------------------------------------------------------------

As of version 0.0.5 of the test build:
The findings on what type of image processing to be used for the features detection of an object is as follows:

1) Template Matching
	Pros:
		1) Can easily identify object feature based on reference images
		2) Can be rotation invariant depending on references images
		3) The quickest and easiest method to implement
	Cons:
		1) It is not brightness invariant, rotation invariant and scale invariant.
		2) Requires a lot of references images for different condition, rotation, angle and scale

2) Shape Matching by Contours
	Pros:
		1) Can easily create boundaries for object feature depending on reference images or data
		2) Quick process
	Cons:
		1) It is not brightness invariant, rotation invariant and scale invariant.
		2) Requires a lot of references images for different condition, rotation, angle and scale

3) Comparing feature hu Moments
	Pros:
		1) Rotation invariant
		2) Quick process
	Cons:
		1) Hard to implement as object feature need to be almost the same as reference image

4) Cascade classifier
	Pros:
		1) Very good at detecting object feature based on training
	Cons:
		1) Training system takes a long time
		2) Not much brigthness invariant, rotation invariant and scale invariant.
		3) Implementation takes time

5) Feature detection algorithm
	Pros:
		1) Can easily detect objects with a lot of features
		2) Can be quick depending on algorithm
		3) Easy to implement
		4) Rotation, Scale and angle invariant!
		5) KAZE algorithm gives the best result but is much slower than the rest
		6) BRISK is fast and can gives quite a good result
		7) ORB and AKAZE is fast but gives bad results on different scale
	Cons:
		1) Can be slow depending on algorithm
		2) Cannot be used to detect a specific object feature
		3) Can have false positives if background environment changes
