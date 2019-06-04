function LabelImSet(imSetFd, subFd, angRt, imgFmt, shft_text, numSpec, endImg, ifSvLbd, ifText)
    % label the input image set folder according to LSP like format.  continues read in the image, update the joints_gt mat and save it every 10 steps. joitns follow LEEDS order. 3rd row stands for visibility. All is 0 in beta version. each columns stands for a coordinate (x,y, ifInv)
    % right click for invisiblility, left and middle for visible. You can specify the numSpec and endImg 
    % to label single images. 
    % input: 
    % imSetFd: indicates the path of the dataset  like  ac2_0 folder (there
    % is images/ fd under it. 
    % subFd, specify the subfolder structure of the image locations, for
    % example 'images' for SYN data 
    % angRt, the counter clockwise rotation angles 
    % imgFmt, the image formate in string format 
    % shft_text, the text shift for visualization , default 15 
    % numSpec, start from, default -1 automatically from last position (indicated by joints_gt)
    % endImg, idx for last image to be labeled, default -1, it will be replaced by the number of rest images. 
    % ifSvLbd: if saved labeled data default 1 
    % ifText: if show the text when labeling, defaults 1 
    % Author Shuangjun Liu
    % history:
    % 1. add text hint to the labeling process to help, add shift to add invisible labels 
    % 18.10.2,  add file structure and rotation post processing. images will
    % be rotated first before labeling, image will also need to be rotated
    % before use. 
    % 18.10.12, rectify r to last point label 
if nargin < 2
    subFd = 'images';    % images sub folder 
end
if nargin < 3
    angRt = 0;    % no rotation 
end
if nargin < 4
    imgFmt = 'jpg'; 
end

if nargin <5
    shft_text = 15;     
end

if nargin < 6
    numSpec = -1;    % replace later 
end
if nargin < 7
    endImg = -1;
end
if nargin < 8 
    ifSvLbd = 0;
end
if nargin <9
    ifText = 1;
end


saveStp = 5;    % how many steps to save joints_gt.mat file 
imFd = fullfile(imSetFd, subFd);    
lbdFd = fullfile(imSetFd,'labeled'); % labeled image for reference later 

if ~exist(lbdFd) && ifSvLbd
    mkdir(lbdFd);
end

fileList = dir(fullfile(imFd,strcat('*.', imgFmt)));
fileLs = fileList(not([fileList.isdir]));

nImgsInFd = length(fileLs); 
fprintf('%d images found in set %s \n',endImg,imSetFd);

if -1 == endImg  % get total 
    endNum = nImgsInFd;
else
    endNum = endImg;
end
if endNum> nImgsInFd;    % check nImgs 
    error('there is less images in Fd than indicated by nImgs as %d', nImgs);
end

numExist = 0;   
% if there is joints_gt.mat there read in to continue 
if exist(fullfile(imSetFd,'joints_gt.mat')) 
    fprintf('previous labeling exist \n');
    matCont = load(fullfile(imSetFd,'joints_gt.mat'));
    joints_gt = matCont.joints_gt;
    numExist = size(joints_gt,3);
    fprintf('load previous labeling time')
    matCont = load(fullfile(imSetFd,'labelTms.mat'));
    labelTms = matCont.labelTms;        % get privioius one 
    fprintf('%d labels exist \n',numExist);
else
    fprintf('new lableing \n');
%     jonits_gt = zeros(3,14, endNum);
    joints_gt = [];
    labelTms = zeros(1,endNum);       
end

if -1 == numSpec
    stId = numExist+1;
else
    stId = numSpec
end

if stId - numExist>1    % more than one difference
    error('Attention! there is gap in the label data, check start point');
end
% where to ends

if endNum < stId
    error('starting number %d is bigger than end number %d \n possibly already numbered', stId, endNum);
    
end
% give all joints in sequence 
jtNms = {'r\_ak','r\_knee','r\_hip','l\_hip','l\_knee','l\_ank','r\_wrist','r\_ebl','r\_shd','l\_shd','l\_ebl','l\_wrist','neck','head'};
% which direction to align the text, 1 for left, 2 for right, subjects usually face us, so 1 for left part, 2 for right part
idxsAlign = [2,2,2,1,1,1,2,2,2,1,1,1,2,2]; % head and nect for left 

figure(1); 
set(gcf, 'pointer', 'crosshair');

for i = stId:endNum
    flgReDraw = 1;
    % imNm = sprintf('image_%06d.png',i);
    fprintf('read in %d-th file %s \n',i, fileLs(i).name); 
    I = imread(fullfile(imFd,fileLs(i).name));
    I = imrotate(I, angRt);
    figure(1); 
    jointsT = [];
    while(flgReDraw)        % this to repeat checking 
        cla;    % clean each time 
        fprintf('processing image %d\n',i);
        figure(1);imshow(I);
        hold on;
        tic
        % while size(jointsT, 1) < 14 keep on get point 
%         for j = 1:14 % 14 joints 
        while(size(jointsT,2)<14)
            % update existing joints plot 
           
            figure(1);
            imshow(I);
            hold on;
            if ~isempty(jointsT)
                plot(jointsT(1,:), jointsT(2,:),'g.');
                for k = 1: size(jointsT,2)
                    x = jointsT(1,k);
                    y = jointsT(2,k);
                    if jointsT(3,k) 
                        clrStr = 'r';
                    else
                        clrStr = 'g';
                    end

                    if 2 == idxsAlign(k) 
                        alignStr = 'left';
                        x_bias = -shft_text; % bias from the points
                    else
                        alignStr = 'right';
                        x_bias = shft_text; 
                    end
                     text(x + x_bias,y, jtNms{k},'HorizontalAlignment', alignStr,'color',clrStr,'fontSize',12);
                end
            end
            
            [x,y,button] = ginput(1);

            if 3== button
                inVis = 1;  
%                 clrStr = 'r';
            elseif 'r' == button
                ifRe = 1;       % redraw 
                fprintf('Redo joint %d',size(jointsT,2)-1);
                jointsT(:,end) = [];    % empty last column
                continue;
            elseif 'e' == button
                fprintf('user exit');
                close all
                return
            else                
                inVis = 0;
%                 clrStr = 'g';
            end
%             jointsT(:,j)=[x;y;inVis];       % 1 for invisible 
            jointsT = [ jointsT, [x;y;inVis]];
        end
        LabelTm_tmp = toc;  % this round time 
              
        % draw the skeletons         
        plot([jointsT(1,1),jointsT(1,2)],[jointsT(2,1),jointsT(2,2)],'r','LineWidth',1);hold on;
        plot([jointsT(1,2),jointsT(1,3)],[jointsT(2,2),jointsT(2,3)],'y','LineWidth',1);hold on;
        plot([jointsT(1,3),jointsT(1,4)],[jointsT(2,3),jointsT(2,4)],'b','LineWidth',1);hold on;
        plot([jointsT(1,4),jointsT(1,5)],[jointsT(2,4),jointsT(2,5)],'y','LineWidth',1);hold on;
        plot([jointsT(1,5),jointsT(1,6)],[jointsT(2,5),jointsT(2,6)],'r','LineWidth',1);hold on;
        plot([jointsT(1,7),jointsT(1,8)],[jointsT(2,7),jointsT(2,8)],'r','LineWidth',1);hold on;
        plot([jointsT(1,8),jointsT(1,9)],[jointsT(2,8),jointsT(2,9)],'y','LineWidth',1);hold on;
        plot([jointsT(1,9),jointsT(1,10)],[jointsT(2,9),jointsT(2,10)],'b','LineWidth',1);hold on;
        plot([jointsT(1,10),jointsT(1,11)],[jointsT(2,10),jointsT(2,11)],'y','LineWidth',1);hold on;
        plot([jointsT(1,11),jointsT(1,12)],[jointsT(2,11),jointsT(2,12)],'r','LineWidth',1);hold on;
        plot([jointsT(1,13),jointsT(1,14)],[jointsT(2,13),jointsT(2,14)],'b','LineWidth',1);hold on;

%        key = get(gcf,'CurrentKey');
       keyIn = input('continue[1] or redo [2]');
       if (keyIn ==1)
           flgReDraw = 0;   % clear up 
           fprintf('label succeed\n');
           % update joints_gt
           joints_gt(:,:,i) = jointsT;
           % save current image to labeled folder
%            imwrite(fullfile(lbdFd,imNm))
            labelTms(i) = LabelTm_tmp;
            fprintf('Label time costs %d secs for image %d of %d \n', LabelTm_tmp, i, endNum);
            if ifSvLbd   % labeled images can be generated in batch later.
                SaveFigPng(figure(1),fullfile(lbdFd,fileLs(i).name));
            end
       else
           fprintf('redo this label\n');           
       end        
    end
    if mod(i,saveStp)==0
        save(fullfile(imSetFd,'joints_gt.mat'),'joints_gt');
        save(fullfile(imSetFd, 'labelTms.mat'),'labelTms');
        fprintf('joints_gt.mat file updated at %d \n',i);
    end
end
avTm = mean(labelTms(labelTms>0));  
fprintf('Job done. Average time cost is %f s \n', avTm);
fprintf('from %d to %d files labeled \n',stId,endNum);
save(fullfile(imSetFd,'joints_gt.mat'),'joints_gt');
% save labelTms here 
save(fullfile(imSetFd, 'labelTms.mat'), 'labelTms');