#!/usr/bin/env python

# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Tokyo Opensource Robotics Kyokai Association
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Tokyo Opensource Robotics Kyokai Association. nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Author: Isaac Isao Saito

import rospy


class BaseHands(object):
    '''
    This class provides methods that are generic for the hands of
    Kawada Industries' dual-arm robot called Nextage Open.

    DIO pin numbers are set in
    nextage_ros_bridge.abs_hand_command.AbsractHandCommand
    '''
    # TODO: Unittest is needed!!

    # Since NEXTAGE is expected to be dual-arm, arm indicator can be defined
    # at the top level of hierarchy.
    HAND_L = '1'  # '0' is expected to be "Both hands".
    HAND_R = '2'

    def __init__(self, parent):
        '''
        Since this class operates requires an access to
        hrpsys.hrpsys_config.HrpsysConfigurator, valid 'parent' is a must.
        Otherwise __init__ returns without doing anything.

        @type parent: hrpsys.hrpsys_config.HrpsysConfigurator
        @param parent: derived class of HrpsysConfigurator.
        '''
        if not parent:
            return  # TODO: Replace with throwing exception
        self._parent = parent

    def _dio_writer(self, digital_out, dio_assignments, padding=1):
        '''
        This private method calls HrpsysConfigurator.writeDigitalOutputWithMask,
        which this class expects to be available via self._parent.

        According to the current (Oct 2013) hardware spec, numbering rule
        differs regarding 0 (numeric figure) in dout and mask as follows:

           * 0 is "ON" in the digital output.
           * 0 is "masked" and not used in mask.

        @type digital_out: int[]
        @param digital_out: Array of indices of digital output that NEED to be
                            flagged as 1.
                            eg. If you're targetting on 25 and 26th places in
                                the DIO array but only 25th is 1, then the
                                array becomes [24].
        @type dio_assignments: int[]
        @param dio_assignments: range(32). This number corresponds to the
                               assigned digital pin of the robot.

                               eg. If the target pin are 25 and 26,
                                   dio_assignments = [24, 25]
        @param padding: Either 0 or 1. Signal arrays will be filled with this
                        value.
        '''

        # 32 bit arrays used in write methods in hrpsys/hrpsys_config.py
        p = padding
        dout = []
        for i in range(32):
            dout.append(p)
        mask = []
        for i in range(32):
            mask.append(0)

        signal_alternate = 0
        if padding == 0:
            signal_alternate = 1
        for i in digital_out:
            dout[i - 1] = signal_alternate

        for i in dio_assignments:
            # For masking, alternate symbol is always 1.
            mask[i - 1] = 1

        # For convenience only; to show array number.
        print_index = []
        for i in range(10):
            # For masking, alternate symbol is always 1.
            n = i + 1
            if 10 == n:
                n = 0
            print_index.append(n)
        print_index.extend(print_index)
        print_index.extend(print_index)
        del print_index[-8:]

        # # For some reason rospy.loginfo not print anything.
        # rospy.loginfo('dout={}, mask={}'.format(dout, mask))
        # # With this print formatting, you can copy the output and paste
        # # directly into writeDigitalOutputWithMask method if you wish.
        rospy.loginfo('dout, mask:\n{},\n{}\n{}'.format(dout, mask,
                                                        print_index))
        try:
            self._parent.writeDigitalOutputWithMask(dout, mask)
        except AttributeError as e:
            rospy.logerr('AttributeError from robot.\nTODO: Needs handled.')
            rospy.logerr('\t{}'.format("Device was not found. Maybe you're" +
                                       "on simulator?"))

    def init_dio(self):
        '''
        Initialize dio. All channels will be set '1' (off), EXCEPT for
        tool changers (channel 19 and 24) so that attached tools won't fall.
        '''
        # TODO: The behavior might not be optimized. Ask Hajime-san and
        #       Nagashima-san to take a look.

        # 10/24/2013 OUT19, 24 are alternated; When they turned to '1', they
        # are ON. So they won't fall upon this function call.

        dout = mask = []
        # Use all slots from 17 to 32.
        for i in range(16, 32):
            mask.append(i)

        self._dio_writer(dout, mask, 0)
