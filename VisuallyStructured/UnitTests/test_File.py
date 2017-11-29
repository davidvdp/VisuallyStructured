import unittest
from Grabbers.File import FileGrabber
from Variables import ImageVar,PathVar

class TestFileGrabber(unittest.TestCase):
    def test_initialization(self):
        filegrabber = FileGrabber()
        self.assertEqual(filegrabber.name, "File")
        self.assertEqual(type(filegrabber.SubVariables["Dir_or_File"]), type(PathVar()))
        self.assertEqual(type(filegrabber.OutputVars["Image"]),type(ImageVar()))

    def test_imageload(self):
        filegrabber = FileGrabber()
        filegrabber.DirOrFile = "..\TestImages\Image3.jpg"
        filegrabber.Execute()
        self.assertEqual(filegrabber.OutputVars["Image"].value.shape[0],200,"Images size does not match")
        self.assertEqual(filegrabber.OutputVars["Image"].value.shape[1],400,"Images size does not match")

        filegrabber.DirOrFile = "..\TestImages"
        previoussize = -1
        for i in range(4):
            filegrabber.Execute()
            self.assertGreater(filegrabber.OutputVars["Image"].value.shape[0], 0)
            self.assertGreater(filegrabber.OutputVars["Image"].value.shape[1], 0)
            self.assertNotEqual(previoussize,filegrabber.OutputVars["Image"].value.shape[1])
            previoussize = filegrabber.OutputVars["Image"].value.shape[1]

if __name__ == "__main__":
    unittest.main()