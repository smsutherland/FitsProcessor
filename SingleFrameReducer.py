import numpy as np
import Image
from glob import glob
from typing import Union, List

class SingleFrameReducer:
    """
    Processor for FITS data processing.

    Stores data relevant to the processing.
    """

    _bias_frame: Image.Image = None
    _dark_current_frame: Image.Image = None
    _normalized_flat_frame: Image.Image = None
    
    def set_bias_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        Set the bias of the processor from filenames.

        Files provided will be averaged on a per-pixel basis to form a single
        bias frame. Frames provided should have as short an exposure time as
        possible.

        Parameters
        ----------
        file_name : str, List[str]
            The filename or list of filenames to use as bias frames. All
            provided names will be expanded in the unix style using glob.
        """

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        bias_frames = [Image.from_file(fname) for fname in file_name_list]
        self._bias_frame = np.mean(bias_frames, axis=0)

    def set_dark_current_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        Set the dark current frames of the processor from filenames.

        Files are all bias-subtracted, then divided by their exposure time to
        find the dark current rate on a per-pixel base. The rate for each frame
        is averaged on a per-pixel basis to form an image representing the
        per-pixel dark current rate. Frames provided should ideally have a long
        exposure time.

        Parameters
        ----------
        file_name : str, List[str]
            The filename or list of filenames to use as dark current frames.
            All provided names will be expanded in the unix style using glob.
        
        Notes
        -----
        set_bias_frames is required to be called before calling this function.
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before calling this function")

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        dark_current_frames_full = [Image.from_file(fname, True) for fname in file_name_list]
        dark_current_frames_bias_subtracted = [self.bias_subtract(frame[0]) for frame in dark_current_frames_full]

        exposure_times = [frame[1]["EXPTIME"] for frame in dark_current_frames_full]
        for frame, exposure_time in zip(dark_current_frames_bias_subtracted, exposure_times):
            frame = frame/exposure_time
        self._dark_current_frame = np.mean(dark_current_frames_bias_subtracted, axis=0)
    
    def set_flat_frames(self, file_name: Union[str, List[str]]) -> None:
        """
        Set the flat frames of the processor from filenames.

        Files are dark-subtracted, then all files are averaged on a per-pixel
        basis. The result is normalized and stored as the flat frame.

        Parameters
        ----------
        file_name : str, List[str]
            The filename or list of filenames to use as dark current frames.
            All provided names will be expanded in the unix style using glob.

        Notes
        -----
        set_bias_frames and set_dark_current_frames are required to be called
        before calling this function.
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before calling this function")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before calling this function")

        file_name_list = []
        if isinstance(file_name, list):
            for fname in file_name:
                file_name += glob(fname)
        else:
            file_name_list = glob(file_name)
        
        if len(file_name_list) == 0:
            raise Exception("No files specified or file not found.")
        
        flat_frames_full = [Image.from_file(fname, True) for fname in file_name_list]
        flat_frames_dark_subtracted = [self.dark_subtract(frame[0], frame[1]["EXPTIME"]) for frame in flat_frames_full]
        mean_flat_frame = np.mean(flat_frames_dark_subtracted, axis=0)
        self._normalized_flat_frame = mean_flat_frame/np.mean(mean_flat_frame)

    
    def bias_subtract(self, frame: Image.Image) -> Image.Image:
        """
        Subtract bias from an Image.

        Bias frame is subtracted from the provided Image.

        Parameters
        ----------
        frame : Image
            Image to subtract bias from.
        
        Returns
        -------
        result : Image
            Bias subtracted frame.
        
        Notes
        -----
        set_bias_frames is required to be called before calling this function.
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        
        return frame - self._bias_frame

    def dark_subtract(self, frame: Image.Image, exposure_time: float) -> Image.Image:
        """
        Subtract bias and dark current from an Image.

        Bias frame and dark current frame times exposure time is subtracted
        from the provided Image.

        Parameters
        ----------
        frame : Image
            Image to subtract bias and dark current from.
        exposure_time: float
            Exposure time of the Image being processed.
        
        Returns
        -------
        result : Image
            Dark subtracted frame.
        
        Notes
        -----
        set_bias_frames and set_dark_current_frames are required to be called
        before calling this function.
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before bias subtracting")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before dark subtracting")
        
        return self.bias_subtract(frame) - exposure_time*self._dark_current_frame
    
    def flatten(self, frame: Image.Image, exposure_time: float) -> Image.Image:
        """
        Dark subtract and flatten an Image.

        Subtract bias and dark current from a frame, then divides by the
        normalized flat frame.

        Parameters
        ----------
        frame : Image
            Image to flatten.
        exposure_time : float
            Exposure time of the Image being processed.
        
        Returns
        -------
        result : Image
            Flattened frame.

        Notes
        -----
        set_bias_frames, set_dark_current_frames, and set_flat_frames are
        required to be called before calling this function.
        """

        if self._bias_frame is None:
            raise Exception("call set_bias_frames before flattening")
        if self._dark_current_frame is None:
            raise Exception("call set_dark_current_frames before flattening")
        if self._normalized_flat_frame is None:
            raise Exception("set set_flat_frames before flattening")
        
        return self.dark_subtract(frame, exposure_time)/self._normalized_flat_frame

    def bias_frame(self) -> Image.Image:
        """
        Return a copy of the bias frame.

        Returns
        -------
        result : Image
            Copy of the stored bias frame.
        """

        return np.copy(self._bias_frame)
    
    def dark_current_frame(self) -> Image.Image:
        """
        Return a copy of the dark current rate frame.

        Returns
        -------
        result : Image
            Copy of the stored dark current rate frame.
        """

        return np.copy(self._dark_current_frame)
    
    def flat_frame(self) -> Image.Image:
        """
        Return a copy of the normalized flat frame.

        Returns
        -------
        result : Image
            Copy of the stored normalized flat frame.
        """

        return np.copy(self._normalized_flat_frame)

