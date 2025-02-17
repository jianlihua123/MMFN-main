﻿import functools

import torch
import torch.nn as nn
from torch.nn import init

####################
# initialize
####################

def weights_init_normal(m, std=0.02):
    classname = m.__class__.__name__
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        if classname != "MeanShift":
            print('initializing [%s] ...' % classname)
            init.normal_(m.weight.data, 0.0, std)
            if m.bias is not None:
                m.bias.data.zero_()
    elif isinstance(m, (nn.Linear)):
        init.normal_(m.weight.data, 0.0, std)
        if m.bias is not None:
            m.bias.data.zero_()
    elif isinstance(m, (nn.BatchNorm2d)):
        init.normal_(m.weight.data, 1.0, std)
        init.constant_(m.bias.data, 0.0)

def weights_init_kaiming(m, scale=1):
    classname = m.__class__.__name__
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        if classname != "MeanShift":
            print('initializing [%s] ...' % classname)
            init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
            m.weight.data *= scale
            if m.bias is not None:
                m.bias.data.zero_()
    elif isinstance(m, (nn.Linear)):
        init.kaiming_normal_(m.weight.data, a=0, mode='fan_in')
        m.weight.data *= scale
        if m.bias is not None:
            m.bias.data.zero_()
    elif isinstance(m, (nn.BatchNorm2d)):
        init.constant_(m.weight.data, 1.0)
        m.weight.data *= scale
        init.constant_(m.bias.data, 0.0)

def weights_init_orthogonal(m):
    classname = m.__class__.__name__
    if isinstance(m, (nn.Conv2d, nn.ConvTranspose2d)):
        if classname != "MeanShift":
            print('initializing [%s] ...' % classname)
            init.orthogonal_(m.weight.data, gain=1)
            if m.bias is not None:
                m.bias.data.zero_()
    elif isinstance(m, (nn.Linear)):
        init.orthogonal_(m.weight.data, gain=1)
        if m.bias is not None:
            m.bias.data.zero_()
    elif isinstance(m, (nn.BatchNorm2d)):
        init.normal_(m.weight.data, 1.0, 0.02)
        init.constant_(m.bias.data, 0.0)

def init_weights(net, init_type='kaiming', scale=1, std=0.02):
    # scale for 'kaiming', std for 'normal'.
    print('initialization method [%s]' % init_type)
    if init_type == 'normal':
        weights_init_normal_ = functools.partial(weights_init_normal, std=std)
        net.apply(weights_init_normal_)
    elif init_type == 'kaiming':
        weights_init_kaiming_ = functools.partial(weights_init_kaiming, scale=scale)
        net.apply(weights_init_kaiming_)
    elif init_type == 'orthogonal':
        net.apply(weights_init_orthogonal)
    else:
        raise NotImplementedError('initialization method [%s] is not implemented' % init_type)

####################
# define network
####################

def create_model(opt):
    if opt['mode'] == 'sr':
        net = define_net(opt['networks'])
        return net
    else:
        raise NotImplementedError("The mode [%s] of networks is not recognized." % opt['mode'])

# choose one network
def define_net(opt):

    which_model = opt['which_model'].upper()
    print('===> Building network [%s]...'%which_model)

######## Ablation Study of Diffrent Scales #############

    if which_model.find("MMF") >= 0:  # Dual Scale
        from .mfps_arch import MMF
        net = MMF(in_channels=opt['in_channels'], out_channels=opt['out_channels'],
                                  num_features=opt['num_features'], num_steps=opt['num_steps'], num_groups=opt['num_groups'],
                                  upscale_factor=opt['scale'])
    elif which_model.find('MFPS') >= 0 :  # Single Scale
        from  .mfps_arch import MFPS
        net = MFPS(in_channels=opt['in_channels'], out_channels=opt['out_channels'],
                                  num_features=opt['num_features'], num_steps=opt['num_steps'], num_groups=opt['num_groups'],
                                  upscale_factor=opt['scale'])
    elif which_model.find('MFTHREE') >= 0 :  # Three Scale
        from  .mfps_arch import MMFTHREE
        net = MMFTHREE(in_channels=opt['in_channels'], out_channels=opt['out_channels'],
                                  num_features=opt['num_features'], num_steps=opt['num_steps'], num_groups=opt['num_groups'],
                                  upscale_factor=opt['scale'])


######## Ablation Study of Diffrent Streams #############

    elif which_model.find('MFMSPAN') >= 0: # Dual Stream

        from .mfps_arch import MMFMsPan

        net = MMFMsPan(in_channels=opt['in_channels'], out_channels=opt['out_channels'],

                                  num_features=opt['num_features'], num_steps=opt['num_steps'], num_groups=opt['num_groups'],

                                  upscale_factor=opt['scale'])

    elif which_model.find('MFMSCATPAN') >= 0: # Single Stream

        from .mfps_arch import MMFMsCatPan

        net = MMFMsCatPan(in_channels=opt['in_channels'], out_channels=opt['out_channels'],

                                  num_features=opt['num_features'], num_steps=opt['num_steps'], num_groups=opt['num_groups'],

                                  upscale_factor=opt['scale'])

    else:
        raise NotImplementedError("Network [%s] is not recognized." % which_model)

    if torch.cuda.is_available():
        net = nn.DataParallel(net).cuda()

    return net
