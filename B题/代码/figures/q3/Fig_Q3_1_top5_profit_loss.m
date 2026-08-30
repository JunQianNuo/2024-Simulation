%% Fig.Q3-1  Top 5 可行策略利润及相对最优损失
% 直接读取 results/q3/top10_policies.csv；不保存图片文件。
clear; close all; clc;

here = fileparts(mfilename('fullpath'));
dataDir = fullfile(here, '..', '..', 'results', 'q3');
T = readtable(fullfile(dataDir, 'top10_policies.csv'), 'VariableNamingRule', 'preserve');
T = T(strcmp(string(T.status), 'SUCCESS_EXACT'), :);
T = sortrows(T, 'expected_profit', 'descend');
T = T(1:min(5,height(T)), :);
bestProfit = max(T.expected_profit);
loss = bestProfit - T.expected_profit;

ids = string(T.strategy_id); bits = string(T.strategy_bits);
labels = cell(height(T),1);
for i = 1:height(T), labels{i} = sprintf('%s\n%s', ids(i), bits(i)); end

fig = figure('Color','w', 'Name','Fig.Q3-1 Top5 策略', 'NumberTitle','off');
tiledlayout(fig, 1, 2, 'TileSpacing','compact', 'Padding','compact');

ax1 = nexttile; hold(ax1,'on');
profit = T.expected_profit;
b1 = barh(ax1, 1:height(T), profit, 0.62, 'FaceColor','flat', ...
    'EdgeColor',[0.15 0.15 0.15], 'LineWidth',0.4);
b1.CData = repmat([0.12 0.35 0.58],height(T),1); b1.CData(1,:) = [0.10 0.55 0.32];
set(ax1,'YTick',1:height(T),'YTickLabel',labels,'YDir','reverse', ...
    'FontName',fontNameCN(),'FontSize',9,'Box','off','LineWidth',0.8,'Color','w', ...
    'XColor',[0.12 0.12 0.12],'YColor',[0.12 0.12 0.12]);
xlabel(ax1,'期望利润（元/件）','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]);
title(ax1,'(a) Top 5 策略利润','FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);
xlim(ax1,[0, max(profit)*1.12]); grid(ax1,'on'); ax1.GridAlpha=0.16; ax1.Layer='top';
for i = 1:height(T)
    text(ax1, profit(i)+0.18, i, sprintf('%.3f',profit(i)), ...
        'VerticalAlignment','middle','FontName','Times New Roman','FontSize',9,'Color',[0.12 0.12 0.12]);
end

ax2 = nexttile; hold(ax2,'on');
b2 = barh(ax2, 1:height(T), loss, 0.62, 'FaceColor',[0.85 0.47 0.18], ...
    'EdgeColor',[0.15 0.15 0.15], 'LineWidth',0.4);
set(ax2,'YTick',1:height(T),'YTickLabel',labels,'YDir','reverse', ...
    'FontName',fontNameCN(),'FontSize',9,'Box','off','LineWidth',0.8,'Color','w', ...
    'XColor',[0.12 0.12 0.12],'YColor',[0.12 0.12 0.12]);
xlabel(ax2,'相对最优损失 \Delta\Pi（元/件）','FontName',fontNameCN(),'Color',[0.12 0.12 0.12]);
title(ax2,'(b) 相对最优损失','FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);
xlim(ax2,[0, max(max(loss),eps)*1.35]); grid(ax2,'on'); ax2.GridAlpha=0.16; ax2.Layer='top';
for i = 1:height(T)
    text(ax2, loss(i)+0.03*max(max(loss),1), i, sprintf('\\Delta\\Pi=%.3f',loss(i)), ...
        'VerticalAlignment','middle','FontName','Times New Roman','FontSize',9,'Color',[0.12 0.12 0.12]);
end
sgtitle(fig,'问题三 Top 5 可行固定策略：利润与相对最优损失', ...
    'FontName',fontNameCN(),'FontWeight','normal','Color',[0.12 0.12 0.12]);

function name = fontNameCN()
fonts = listfonts;
candidates = {'Noto Serif CJK SC','Source Han Serif SC','SimSun','Songti SC','Microsoft YaHei'};
name = 'DejaVu Serif';
for i = 1:numel(candidates)
    if any(strcmpi(fonts, candidates{i})), name = candidates{i}; return; end
end
end
