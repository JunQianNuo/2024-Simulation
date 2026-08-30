%% Fig.Q3-2  关键参数敏感性与策略切换
% 官方缺陷率范围与人为设置的 +/-25%% 成本压力测试分面显示。
clear; close all; clc;

here = fileparts(mfilename('fullpath'));
dataDir = fullfile(here, '..', '..', 'results', 'q3');
T = readtable(fullfile(dataDir, 'sensitivity.csv'), 'VariableNamingRule', 'preserve');
defectBasis = 'official Table 1-2 observed defect-rate range';
costBasis = 'hypothetical +/-25% cost stress scenario';
D = T(strcmp(string(T.range_basis), defectBasis), :);
C = T(strcmp(string(T.range_basis), costBasis), :);
rowNames = {'part_1','part_2','part_3','part_4','part_5','part_6','part_7','part_8', ...
            'semi_1','semi_2','semi_3','final'};
rowLabels = {'p_1','p_2','p_3','p_4','p_5','p_6','p_7','p_8', ...
             'p_{S1}','p_{S2}','p_{S3}','p_F'};
costNames = {'part_inspection','semi_inspection','final_inspection', ...
             'replacement','semi_disassembly','final_disassembly'};
costLabels = {'零件检测','半成品检测','成品检测','调换损失','半成品拆解','成品拆解'};
defectValues = [0.05 0.20]; costValues = [0.75 1.25];

defectGap = nan(numel(rowNames),2); defectSwitch = false(numel(rowNames),2);
for i = 1:numel(rowNames)
    rows = D(strcmp(string(D.parameter),rowNames{i}), :);
    for j = 1:2
        row = rows(abs(rows.value_or_multiplier - defectValues(j)) < 1e-10, :);
        if height(row) == 1
            defectGap(i,j) = row.profit_gap_to_second;
            defectSwitch(i,j) = asLogical(row.nominal_strategy_changed);
        end
    end
end
costGap = nan(numel(costNames),2); costSwitch = false(numel(costNames),2);
for i = 1:numel(costNames)
    rows = C(strcmp(string(C.parameter),costNames{i}), :);
    for j = 1:2
        row = rows(abs(rows.value_or_multiplier - costValues(j)) < 1e-10, :);
        if height(row) == 1
            costGap(i,j) = row.profit_gap_to_second;
            costSwitch(i,j) = asLogical(row.nominal_strategy_changed);
        end
    end
end

fig = figure('Color','w', 'Name','Fig.Q3-2 敏感性与策略切换', 'NumberTitle','off');
tiledlayout(fig,1,2,'TileSpacing','compact','Padding','compact');

ax1 = nexttile; imagesc(ax1, defectGap); set(ax1,'YDir','normal');
colormap(ax1, parula(256)); caxis(ax1,[0 max(defectGap(:),[],'omitnan')]);
set(ax1,'XTick',1:2,'XTickLabel',{'5%','20%'},'YTick',1:numel(rowNames), ...
    'YTickLabel',rowLabels,'FontName',fontNameCN(),'FontSize',9,'Box','off','Color','w', ...
    'XColor',[0.12 0.12 0.12],'YColor',[0.12 0.12 0.12]);
xlabel(ax1,'缺陷率取值','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]); ylabel(ax1,'质量参数','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]);
title(ax1,'(a) 缺陷率敏感性','FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);
cb1=colorbar(ax1); cb1.Label.String='利润间隔 \\Delta\\Pi（元/件）'; cb1.FontName='Times New Roman'; cb1.Color=[0.12 0.12 0.12];
annotateHeatmap(ax1, defectGap, defectSwitch);

ax2 = nexttile; imagesc(ax2, costGap); set(ax2,'YDir','normal');
colormap(ax2, parula(256)); caxis(ax2,[0 max(costGap(:),[],'omitnan')]);
set(ax2,'XTick',1:2,'XTickLabel',{'-25%','+25%'},'YTick',1:numel(costNames), ...
    'YTickLabel',costLabels,'FontName',fontNameCN(),'FontSize',9,'Box','off','Color','w', ...
    'XColor',[0.12 0.12 0.12],'YColor',[0.12 0.12 0.12]);
xlabel(ax2,'成本相对基准的变化','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]); ylabel(ax2,'成本参数','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]);
title(ax2,'(b) 成本压力测试','FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);
cb2=colorbar(ax2); cb2.Label.String='利润间隔 \\Delta\\Pi（元/件）'; cb2.FontName='Times New Roman'; cb2.Color=[0.12 0.12 0.12];
annotateHeatmap(ax2, costGap, costSwitch);
sgtitle(fig,'问题三关键参数敏感性与策略切换','FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);
annotation(fig,'textbox',[0.17 0.005 0.67 0.035],'String', ...
    '数值为最优策略与次优策略的利润间隔；★表示该场景相对名义策略发生切换。', ...
    'EdgeColor','none','HorizontalAlignment','center','FontName',fontNameCN(),'FontSize',9,'Color',[0.12 0.12 0.12]);

function annotateHeatmap(ax, values, switches)
for i = 1:size(values,1)
    for j = 1:size(values,2)
        if isfinite(values(i,j))
            if values(i,j) > 0.55*max(values(:),[],'omitnan'), txtColor=[1 1 1]; else, txtColor=[0.1 0.1 0.1]; end
            mark = ''; if switches(i,j), mark=' ★'; end
            text(ax,j,i,sprintf('%.3f%s',values(i,j),mark),'HorizontalAlignment','center', ...
                'FontName','Times New Roman','FontSize',8,'Color',txtColor,'FontWeight','bold');
        end
    end
end
end

function value = asLogical(raw)
if iscell(raw), raw = raw{1}; end
if isstring(raw) || ischar(raw), value = strcmpi(string(raw),'true');
else, value = logical(raw); end
end

function name = fontNameCN()
fonts = listfonts;
candidates = {'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name = 'DejaVu Serif';
for i = 1:numel(candidates)
    if any(strcmpi(fonts, candidates{i})), name = candidates{i}; return; end
end
end
