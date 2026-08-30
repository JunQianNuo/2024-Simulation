%% Fig.Q4-2  Q3 各质量参数的边际净 KG
clear; close all; clc;
here=fileparts(mfilename('fullpath')); dataDir=fullfile(here,'..','..','results','q4');
T=readtable(fullfile(dataDir,'q3_kg_action_values.csv'),'VariableNamingRule','preserve'); T=T(~strcmp(string(T.action),'STOP'),:);
names={'part_1','part_2','part_3','part_4','part_5','part_6','part_7','part_8','semi_1','semi_2','semi_3','final'};
labels={'零件1','零件2','零件3','零件4','零件5','零件6','零件7','零件8','半成品1','半成品2','半成品3','最终成品'};
fig=figure('Color','w','Name','Fig.Q4-2 Q3净KG','NumberTitle','off'); tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact'); ink=[.12 .12 .12];
priors={'uniform','jeffreys'};
for q=1:2
    ax=nexttile; hold(ax,'on'); R=T(strcmp(string(T.prior),priors{q}),:); [~,idx]=ismember(names,string(R.action)); R=R(idx,:);
    x=R.net_KG; lo=R.net_KG_CI_lower; hi=R.net_KG_CI_upper; y=1:numel(names);
    errorbar(ax,x,y,x-lo,hi-x,'horizontal','o','Color',[.12 .35 .58],'MarkerFaceColor',[.12 .35 .58],'LineWidth',1.0,'CapSize',5);
    xline(ax,0,'--','Color',[.78 .18 .16],'LineWidth',1.1);
    set(ax,'YTick',y,'YTickLabel',labels,'YDir','reverse','Color','w','XColor',ink,'YColor',ink,'Box','off','FontName',fontNameCN(),'FontSize',9);
    xlabel(ax,'Net KG（元/件）','FontName',fontNameCN(),'Color',ink); title(ax,sprintf('(%c) %s prior',char('a'+q-1),priors{q}),'FontName',fontNameCN(),'FontWeight','normal','Color',ink);
    grid(ax,'on'); ax.GridAlpha=.16;
end
sgtitle(fig,'演示抽样情景下问题三各质量参数的边际净信息价值（一步 KG）','FontName',fontNameCN(),'FontWeight','normal','Color',ink);
annotation(fig,'textbox',[.16 .005 .68 .035],'String','误差棒为独立确认批次给出的净 KG 区间；当前所有参数的上界均低于 0。','EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',9,'Color',ink);

function name=fontNameCN()
fonts=listfonts; candidates={'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'}; name='DejaVu Serif';
for i=1:numel(candidates), if any(strcmpi(fonts,candidates{i})), name=candidates{i}; return; end, end
end
